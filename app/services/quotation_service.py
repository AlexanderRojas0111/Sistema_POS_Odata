"""
Quotation Service - Sistema POS Sabrositas
==========================================
Servicio para gestión de cotizaciones y presupuestos.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from app import db
from app.models.quotation import Quotation, QuotationItem, QuotationApproval, QuotationTemplate
from app.models.accounts_receivable import Customer
from app.models.sale import Sale, SaleItem
from app.exceptions import BusinessLogicError, ValidationError

logger = logging.getLogger(__name__)

class QuotationService:
    """Servicio para gestión de cotizaciones"""
    
    def __init__(self):
        self.logger = logger
    
    # ==================== COTIZACIONES ====================
    
    def create_quotation(self, quotation_data: Dict[str, Any]) -> Quotation:
        """Crear nueva cotización"""
        try:
            # Validar datos requeridos
            required_fields = ['customer_id', 'user_id', 'title', 'items']
            
            for field in required_fields:
                if field not in quotation_data or not quotation_data[field]:
                    raise ValidationError(f"Campo requerido: {field}")
            
            # Verificar cliente
            customer = Customer.query.get(quotation_data['customer_id'])
            if not customer:
                raise ValidationError("Cliente no encontrado")
            
            if not customer.is_active:
                raise ValidationError("Cliente inactivo")
            
            # Crear cotización
            quotation = Quotation(
                customer_id=quotation_data['customer_id'],
                user_id=quotation_data['user_id'],
                title=quotation_data['title'],
                description=quotation_data.get('description'),
                quotation_date=quotation_data.get('quotation_date', date.today()),
                valid_until=quotation_data.get('valid_until'),
                priority=quotation_data.get('priority', 'normal'),
                notes=quotation_data.get('notes'),
                terms_conditions=quotation_data.get('terms_conditions'),
                delivery_time=quotation_data.get('delivery_time'),
                payment_terms=quotation_data.get('payment_terms')
            )
            
            db.session.add(quotation)
            db.session.flush()  # Para obtener el ID
            
            # Crear items de la cotización
            for item_data in quotation_data['items']:
                item = QuotationItem(
                    quotation_id=quotation.id,
                    product_id=item_data.get('product_id'),
                    product_name=item_data['product_name'],
                    product_code=item_data.get('product_code'),
                    description=item_data.get('description'),
                    quantity=Decimal(str(item_data['quantity'])),
                    unit_price=Decimal(str(item_data['unit_price'])),
                    discount_percentage=Decimal(str(item_data.get('discount_percentage', 0))),
                    notes=item_data.get('notes'),
                    delivery_time=item_data.get('delivery_time')
                )
                
                # Calcular totales del item
                item.calculate_totals()
                db.session.add(item)
            
            # Calcular totales de la cotización
            quotation.calculate_totals()
            
            # Agregar impuestos y descuentos si se especifican
            quotation.tax_amount = Decimal(str(quotation_data.get('tax_amount', 0)))
            quotation.discount_amount = Decimal(str(quotation_data.get('discount_amount', 0)))
            quotation.total_amount = quotation.subtotal + quotation.tax_amount - quotation.discount_amount
            
            db.session.commit()
            
            self.logger.info(f"Cotización creada: {quotation.quotation_number}")
            return quotation
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creando cotización: {str(e)}")
            raise BusinessLogicError(f"Error creando cotización: {str(e)}")
    
    def get_quotation(self, quotation_id: int) -> Optional[Quotation]:
        """Obtener cotización por ID"""
        return Quotation.query.get(quotation_id)
    
    def get_quotations(self, status: str = None, customer_id: int = None, user_id: int = None) -> List[Quotation]:
        """Obtener lista de cotizaciones"""
        query = Quotation.query
        
        if status:
            query = query.filter_by(status=status)
        
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.order_by(Quotation.created_at.desc()).all()
    
    def get_quotations_by_customer(self, customer_id: int) -> List[Quotation]:
        """Obtener cotizaciones por cliente"""
        return Quotation.query.filter_by(customer_id=customer_id).order_by(Quotation.created_at.desc()).all()
    
    def get_expired_quotations(self) -> List[Quotation]:
        """Obtener cotizaciones vencidas"""
        return Quotation.query.filter(
            Quotation.valid_until < date.today(),
            Quotation.status.in_(['draft', 'pending'])
        ).order_by(Quotation.valid_until.asc()).all()
    
    def update_quotation(self, quotation_id: int, quotation_data: Dict[str, Any]) -> Quotation:
        """Actualizar cotización"""
        try:
            quotation = self.get_quotation(quotation_id)
            if not quotation:
                raise ValidationError("Cotización no encontrada")
            
            if quotation.status not in ['draft']:
                raise ValidationError("Solo se pueden editar cotizaciones en borrador")
            
            # Actualizar campos básicos
            for key, value in quotation_data.items():
                if hasattr(quotation, key) and key not in ['id', 'uuid', 'quotation_number', 'created_at', 'items']:
                    setattr(quotation, key, value)
            
            # Actualizar items si se proporcionan
            if 'items' in quotation_data:
                # Eliminar items existentes
                QuotationItem.query.filter_by(quotation_id=quotation_id).delete()
                
                # Crear nuevos items
                for item_data in quotation_data['items']:
                    item = QuotationItem(
                        quotation_id=quotation_id,
                        product_id=item_data.get('product_id'),
                        product_name=item_data['product_name'],
                        product_code=item_data.get('product_code'),
                        description=item_data.get('description'),
                        quantity=Decimal(str(item_data['quantity'])),
                        unit_price=Decimal(str(item_data['unit_price'])),
                        discount_percentage=Decimal(str(item_data.get('discount_percentage', 0))),
                        notes=item_data.get('notes'),
                        delivery_time=item_data.get('delivery_time')
                    )
                    
                    item.calculate_totals()
                    db.session.add(item)
                
                # Recalcular totales
                quotation.calculate_totals()
            
            quotation.updated_at = datetime.utcnow()
            db.session.commit()
            
            self.logger.info(f"Cotización actualizada: {quotation.quotation_number}")
            return quotation
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error actualizando cotización: {str(e)}")
            raise BusinessLogicError(f"Error actualizando cotización: {str(e)}")
    
    def delete_quotation(self, quotation_id: int) -> bool:
        """Eliminar cotización"""
        try:
            quotation = self.get_quotation(quotation_id)
            if not quotation:
                raise ValidationError("Cotización no encontrada")
            
            if quotation.status not in ['draft']:
                raise ValidationError("Solo se pueden eliminar cotizaciones en borrador")
            
            db.session.delete(quotation)
            db.session.commit()
            
            self.logger.info(f"Cotización eliminada: {quotation.quotation_number}")
            return True
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error eliminando cotización: {str(e)}")
            raise BusinessLogicError(f"Error eliminando cotización: {str(e)}")
    
    # ==================== APROBACIÓN ====================
    
    def submit_for_approval(self, quotation_id: int, approver_id: int) -> Quotation:
        """Enviar cotización para aprobación"""
        try:
            quotation = self.get_quotation(quotation_id)
            if not quotation:
                raise ValidationError("Cotización no encontrada")
            
            if not quotation.can_be_approved:
                raise ValidationError("La cotización no puede ser enviada para aprobación")
            
            # Cambiar estado
            quotation.status = 'pending'
            quotation.updated_at = datetime.utcnow()
            
            # Crear registro de aprobación
            approval = QuotationApproval(
                quotation_id=quotation_id,
                approver_id=approver_id,
                action='approve',
                approval_level=1
            )
            
            db.session.add(approval)
            db.session.commit()
            
            self.logger.info(f"Cotización enviada para aprobación: {quotation.quotation_number}")
            return quotation
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error enviando cotización para aprobación: {str(e)}")
            raise BusinessLogicError(f"Error enviando cotización para aprobación: {str(e)}")
    
    def approve_quotation(self, quotation_id: int, approver_id: int, comments: str = None) -> Quotation:
        """Aprobar cotización"""
        try:
            quotation = self.get_quotation(quotation_id)
            if not quotation:
                raise ValidationError("Cotización no encontrada")
            
            if quotation.status != 'pending':
                raise ValidationError("La cotización no está pendiente de aprobación")
            
            # Aprobar cotización
            quotation.status = 'approved'
            quotation.approved_by = approver_id
            quotation.approved_at = datetime.utcnow()
            quotation.updated_at = datetime.utcnow()
            
            # Completar registro de aprobación
            approval = QuotationApproval.query.filter_by(
                quotation_id=quotation_id,
                approver_id=approver_id,
                status='pending'
            ).first()
            
            if approval:
                approval.status = 'completed'
                approval.completed_at = datetime.utcnow()
                approval.comments = comments
            
            db.session.commit()
            
            self.logger.info(f"Cotización aprobada: {quotation.quotation_number}")
            return quotation
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error aprobando cotización: {str(e)}")
            raise BusinessLogicError(f"Error aprobando cotización: {str(e)}")
    
    def reject_quotation(self, quotation_id: int, approver_id: int, rejection_reason: str) -> Quotation:
        """Rechazar cotización"""
        try:
            quotation = self.get_quotation(quotation_id)
            if not quotation:
                raise ValidationError("Cotización no encontrada")
            
            if quotation.status != 'pending':
                raise ValidationError("La cotización no está pendiente de aprobación")
            
            # Rechazar cotización
            quotation.status = 'rejected'
            quotation.rejection_reason = rejection_reason
            quotation.updated_at = datetime.utcnow()
            
            # Completar registro de aprobación
            approval = QuotationApproval.query.filter_by(
                quotation_id=quotation_id,
                approver_id=approver_id,
                status='pending'
            ).first()
            
            if approval:
                approval.action = 'reject'
                approval.status = 'completed'
                approval.completed_at = datetime.utcnow()
                approval.comments = rejection_reason
            
            db.session.commit()
            
            self.logger.info(f"Cotización rechazada: {quotation.quotation_number}")
            return quotation
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error rechazando cotización: {str(e)}")
            raise BusinessLogicError(f"Error rechazando cotización: {str(e)}")
    
    # ==================== CONVERSIÓN A VENTA ====================
    
    def convert_to_sale(self, quotation_id: int, user_id: int) -> Sale:
        """Convertir cotización a venta"""
        try:
            quotation = self.get_quotation(quotation_id)
            if not quotation:
                raise ValidationError("Cotización no encontrada")
            
            if not quotation.can_be_converted:
                raise ValidationError("La cotización no puede ser convertida a venta")
            
            # Crear venta
            sale = Sale(
                user_id=user_id,
                customer_id=quotation.customer_id,
                total_amount=quotation.total_amount,
                notes=f"Convertida desde cotización {quotation.quotation_number}",
                status='completed'
            )
            
            db.session.add(sale)
            db.session.flush()  # Para obtener el ID
            
            # Crear items de la venta
            for quotation_item in quotation.items:
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=quotation_item.product_id,
                    product_name=quotation_item.product_name,
                    product_code=quotation_item.product_code,
                    quantity=quotation_item.quantity,
                    unit_price=quotation_item.unit_price,
                    total_amount=quotation_item.total_amount
                )
                
                db.session.add(sale_item)
            
            # Marcar cotización como convertida
            quotation.converted_to_sale = True
            quotation.sale_id = sale.id
            quotation.converted_at = datetime.utcnow()
            quotation.status = 'converted'
            quotation.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            self.logger.info(f"Cotización convertida a venta: {quotation.quotation_number} -> {sale.id}")
            return sale
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error convirtiendo cotización a venta: {str(e)}")
            raise BusinessLogicError(f"Error convirtiendo cotización a venta: {str(e)}")
    
    # ==================== PLANTILLAS ====================
    
    def create_template(self, template_data: Dict[str, Any]) -> QuotationTemplate:
        """Crear plantilla de cotización"""
        try:
            template = QuotationTemplate(**template_data)
            db.session.add(template)
            db.session.commit()
            
            self.logger.info(f"Plantilla creada: {template.template_name}")
            return template
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creando plantilla: {str(e)}")
            raise BusinessLogicError(f"Error creando plantilla: {str(e)}")
    
    def get_template(self, template_id: int) -> Optional[QuotationTemplate]:
        """Obtener plantilla por ID"""
        return QuotationTemplate.query.get(template_id)
    
    def get_templates(self) -> List[QuotationTemplate]:
        """Obtener plantillas activas"""
        return QuotationTemplate.query.filter_by(is_active=True).all()
    
    def get_default_template(self) -> Optional[QuotationTemplate]:
        """Obtener plantilla por defecto"""
        return QuotationTemplate.query.filter_by(is_default=True, is_active=True).first()
    
    # ==================== REPORTES ====================
    
    def get_quotations_summary(self, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """Obtener resumen de cotizaciones"""
        query = Quotation.query
        
        if start_date:
            query = query.filter(Quotation.quotation_date >= start_date)
        if end_date:
            query = query.filter(Quotation.quotation_date <= end_date)
        
        quotations = query.all()
        
        summary = {
            'total_quotations': len(quotations),
            'total_amount': sum(float(q.total_amount) for q in quotations),
            'by_status': {
                'draft': len([q for q in quotations if q.status == 'draft']),
                'pending': len([q for q in quotations if q.status == 'pending']),
                'approved': len([q for q in quotations if q.status == 'approved']),
                'rejected': len([q for q in quotations if q.status == 'rejected']),
                'expired': len([q for q in quotations if q.is_expired]),
                'converted': len([q for q in quotations if q.converted_to_sale])
            },
            'conversion_rate': 0
        }
        
        # Calcular tasa de conversión
        if summary['total_quotations'] > 0:
            summary['conversion_rate'] = (summary['by_status']['converted'] / summary['total_quotations']) * 100
        
        return summary
    
    def get_quotation_analytics(self, customer_id: int = None) -> Dict[str, Any]:
        """Obtener análisis de cotizaciones"""
        query = Quotation.query
        
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        quotations = query.all()
        
        # Análisis por prioridad
        priority_analysis = {}
        for priority in ['low', 'normal', 'high', 'urgent']:
            priority_quotations = [q for q in quotations if q.priority == priority]
            priority_analysis[priority] = {
                'count': len(priority_quotations),
                'total_amount': sum(float(q.total_amount) for q in priority_quotations),
                'conversion_rate': 0
            }
            
            if len(priority_quotations) > 0:
                converted = len([q for q in priority_quotations if q.converted_to_sale])
                priority_analysis[priority]['conversion_rate'] = (converted / len(priority_quotations)) * 100
        
        # Análisis temporal (últimos 12 meses)
        monthly_analysis = {}
        for i in range(12):
            month_date = date.today().replace(day=1) - timedelta(days=30 * i)
            month_quotations = [q for q in quotations if q.quotation_date.year == month_date.year and q.quotation_date.month == month_date.month]
            
            monthly_analysis[month_date.strftime('%Y-%m')] = {
                'count': len(month_quotations),
                'total_amount': sum(float(q.total_amount) for q in month_quotations),
                'converted': len([q for q in month_quotations if q.converted_to_sale])
            }
        
        return {
            'priority_analysis': priority_analysis,
            'monthly_analysis': monthly_analysis,
            'total_quotations': len(quotations),
            'total_amount': sum(float(q.total_amount) for q in quotations),
            'overall_conversion_rate': (len([q for q in quotations if q.converted_to_sale]) / len(quotations) * 100) if quotations else 0
        }
