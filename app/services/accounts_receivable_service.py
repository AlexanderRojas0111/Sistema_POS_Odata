"""
Accounts Receivable Service - Sistema POS Sabrositas
===================================================
Servicio para gestión de cartera y cuentas por cobrar.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

from app import db
from app.models.accounts_receivable import Customer, Invoice, AccountsReceivableInvoiceItem, Payment, PaymentAllocation
from app.exceptions import BusinessLogicError, ValidationError

logger = logging.getLogger(__name__)

class AccountsReceivableService:
    """Servicio para gestión de cartera"""
    
    def __init__(self):
        self.logger = logger
    
    # ==================== CLIENTES ====================
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Customer:
        """Crear nuevo cliente"""
        try:
            # Validar datos requeridos
            required_fields = ['name', 'document_type', 'document_number']
            
            for field in required_fields:
                if field not in customer_data or not customer_data[field]:
                    raise ValidationError(f"Campo requerido: {field}")
            
            # Verificar que no exista cliente con el mismo documento
            existing_customer = Customer.query.filter_by(
                document_number=customer_data['document_number']
            ).first()
            
            if existing_customer:
                raise ValidationError("Ya existe un cliente con este número de documento")
            
            # Crear cliente
            customer = Customer(**customer_data)
            db.session.add(customer)
            db.session.commit()
            
            self.logger.info(f"Cliente creado: {customer.customer_code}")
            return customer
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creando cliente: {str(e)}")
            raise BusinessLogicError(f"Error creando cliente: {str(e)}")
    
    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Obtener cliente por ID"""
        return Customer.query.get(customer_id)
    
    def get_customer_by_document(self, document_number: str) -> Optional[Customer]:
        """Obtener cliente por número de documento"""
        return Customer.query.filter_by(document_number=document_number).first()
    
    def get_customers(self, active_only: bool = True, customer_type: str = None) -> List[Customer]:
        """Obtener lista de clientes"""
        query = Customer.query
        
        if active_only:
            query = query.filter_by(is_active=True, status='active')
        
        if customer_type:
            query = query.filter_by(customer_type=customer_type)
        
        return query.order_by(Customer.name).all()
    
    def update_customer(self, customer_id: int, customer_data: Dict[str, Any]) -> Customer:
        """Actualizar cliente"""
        try:
            customer = self.get_customer(customer_id)
            if not customer:
                raise ValidationError("Cliente no encontrado")
            
            # Verificar documento único si se está cambiando
            if 'document_number' in customer_data and customer_data['document_number'] != customer.document_number:
                existing = Customer.query.filter_by(
                    document_number=customer_data['document_number']
                ).first()
                if existing and existing.id != customer_id:
                    raise ValidationError("Ya existe un cliente con este número de documento")
            
            # Actualizar campos
            for key, value in customer_data.items():
                if hasattr(customer, key) and key not in ['id', 'uuid', 'customer_code', 'created_at']:
                    setattr(customer, key, value)
            
            customer.updated_at = datetime.utcnow()
            db.session.commit()
            
            self.logger.info(f"Cliente actualizado: {customer.customer_code}")
            return customer
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error actualizando cliente: {str(e)}")
            raise BusinessLogicError(f"Error actualizando cliente: {str(e)}")
    
    def deactivate_customer(self, customer_id: int) -> Customer:
        """Desactivar cliente"""
        try:
            customer = self.get_customer(customer_id)
            if not customer:
                raise ValidationError("Cliente no encontrado")
            
            customer.is_active = False
            customer.status = 'inactive'
            customer.updated_at = datetime.utcnow()
            db.session.commit()
            
            self.logger.info(f"Cliente desactivado: {customer.customer_code}")
            return customer
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error desactivando cliente: {str(e)}")
            raise BusinessLogicError(f"Error desactivando cliente: {str(e)}")
    
    # ==================== FACTURAS ====================
    
    def create_invoice(self, invoice_data: Dict[str, Any]) -> Invoice:
        """Crear nueva factura"""
        try:
            # Validar datos requeridos
            required_fields = ['customer_id', 'user_id', 'items']
            
            for field in required_fields:
                if field not in invoice_data or not invoice_data[field]:
                    raise ValidationError(f"Campo requerido: {field}")
            
            # Verificar cliente
            customer = self.get_customer(invoice_data['customer_id'])
            if not customer:
                raise ValidationError("Cliente no encontrado")
            
            if not customer.is_active:
                raise ValidationError("Cliente inactivo")
            
            # Crear factura
            invoice = Invoice(
                customer_id=invoice_data['customer_id'],
                user_id=invoice_data['user_id'],
                invoice_date=invoice_data.get('invoice_date', date.today()),
                payment_terms=invoice_data.get('payment_terms', customer.payment_terms),
                notes=invoice_data.get('notes'),
                reference=invoice_data.get('reference')
            )
            
            # Calcular fecha de vencimiento
            invoice.due_date = invoice.invoice_date + timedelta(days=invoice.payment_terms)
            
            db.session.add(invoice)
            db.session.flush()  # Para obtener el ID
            
            # Crear items de la factura
            subtotal = Decimal('0.0')
            for item_data in invoice_data['items']:
                item = AccountsReceivableInvoiceItem(
                    invoice_id=invoice.id,
                    product_id=item_data.get('product_id'),
                    product_name=item_data['product_name'],
                    product_code=item_data.get('product_code'),
                    description=item_data.get('description'),
                    quantity=Decimal(str(item_data['quantity'])),
                    unit_price=Decimal(str(item_data['unit_price'])),
                    discount_percentage=Decimal(str(item_data.get('discount_percentage', 0)))
                )
                
                # Calcular descuento y total
                item.discount_amount = (item.quantity * item.unit_price * item.discount_percentage) / 100
                item.total_amount = (item.quantity * item.unit_price) - item.discount_amount
                subtotal += item.total_amount
                
                db.session.add(item)
            
            # Calcular totales
            invoice.subtotal = subtotal
            invoice.tax_amount = Decimal(str(invoice_data.get('tax_amount', 0)))
            invoice.discount_amount = Decimal(str(invoice_data.get('discount_amount', 0)))
            invoice.total_amount = invoice.subtotal + invoice.tax_amount - invoice.discount_amount
            invoice.balance_amount = invoice.total_amount
            invoice.paid_amount = Decimal('0.0')
            
            db.session.commit()
            
            self.logger.info(f"Factura creada: {invoice.invoice_number}")
            return invoice
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creando factura: {str(e)}")
            raise BusinessLogicError(f"Error creando factura: {str(e)}")
    
    def get_invoice(self, invoice_id: int) -> Optional[Invoice]:
        """Obtener factura por ID"""
        return Invoice.query.get(invoice_id)
    
    def get_invoices_by_customer(self, customer_id: int, status: str = None) -> List[Invoice]:
        """Obtener facturas por cliente"""
        query = Invoice.query.filter_by(customer_id=customer_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Invoice.invoice_date.desc()).all()
    
    def get_overdue_invoices(self) -> List[Invoice]:
        """Obtener facturas vencidas"""
        today = date.today()
        return Invoice.query.filter(
            Invoice.due_date < today,
            Invoice.status.in_(['pending', 'partial'])
        ).order_by(Invoice.due_date.asc()).all()
    
    def get_invoices_summary(self, customer_id: int = None) -> Dict[str, Any]:
        """Obtener resumen de facturas"""
        query = Invoice.query
        
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        invoices = query.all()
        
        summary = {
            'total_invoices': len(invoices),
            'total_amount': sum(float(inv.total_amount) for inv in invoices),
            'paid_amount': sum(float(inv.paid_amount) for inv in invoices),
            'pending_amount': sum(float(inv.balance_amount) for inv in invoices),
            'overdue_count': len([inv for inv in invoices if inv.is_overdue]),
            'overdue_amount': sum(float(inv.balance_amount) for inv in invoices if inv.is_overdue)
        }
        
        return summary
    
    # ==================== PAGOS ====================
    
    def create_payment(self, payment_data: Dict[str, Any]) -> Payment:
        """Crear nuevo pago"""
        try:
            # Validar datos requeridos
            required_fields = ['customer_id', 'user_id', 'amount', 'payment_method']
            
            for field in required_fields:
                if field not in payment_data or not payment_data[field]:
                    raise ValidationError(f"Campo requerido: {field}")
            
            # Verificar cliente
            customer = self.get_customer(payment_data['customer_id'])
            if not customer:
                raise ValidationError("Cliente no encontrado")
            
            # Crear pago
            payment = Payment(
                customer_id=payment_data['customer_id'],
                user_id=payment_data['user_id'],
                amount=Decimal(str(payment_data['amount'])),
                payment_method=payment_data['payment_method'],
                payment_date=payment_data.get('payment_date', date.today()),
                reference=payment_data.get('reference'),
                notes=payment_data.get('notes'),
                bank_name=payment_data.get('bank_name'),
                check_number=payment_data.get('check_number')
            )
            
            db.session.add(payment)
            db.session.flush()  # Para obtener el ID
            
            # Asignar pago a facturas si se especifica
            if 'invoice_allocations' in payment_data:
                self._allocate_payment_to_invoices(payment, payment_data['invoice_allocations'])
            
            db.session.commit()
            
            self.logger.info(f"Pago creado: {payment.payment_number}")
            return payment
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creando pago: {str(e)}")
            raise BusinessLogicError(f"Error creando pago: {str(e)}")
    
    def _allocate_payment_to_invoices(self, payment: Payment, allocations: List[Dict[str, Any]]) -> None:
        """Asignar pago a facturas específicas"""
        total_allocated = Decimal('0.0')
        
        for allocation in allocations:
            invoice_id = allocation['invoice_id']
            amount = Decimal(str(allocation['amount']))
            
            # Verificar factura
            invoice = self.get_invoice(invoice_id)
            if not invoice:
                raise ValidationError(f"Factura {invoice_id} no encontrada")
            
            if invoice.customer_id != payment.customer_id:
                raise ValidationError("La factura no pertenece al cliente")
            
            # Crear asignación
            allocation_record = PaymentAllocation(
                payment_id=payment.id,
                invoice_id=invoice_id,
                allocated_amount=amount
            )
            
            db.session.add(allocation_record)
            total_allocated += amount
            
            # Actualizar factura
            invoice.paid_amount += amount
            invoice.calculate_balance()
        
        # Verificar que el total asignado no exceda el pago
        if total_allocated > payment.amount:
            raise ValidationError("El total asignado excede el monto del pago")
        
        # Si no se asignó todo el pago, crear asignación automática
        if total_allocated < payment.amount:
            remaining_amount = payment.amount - total_allocated
            self._auto_allocate_remaining_payment(payment, remaining_amount)
    
    def _auto_allocate_remaining_payment(self, payment: Payment, remaining_amount: Decimal) -> None:
        """Asignar automáticamente el pago restante a facturas vencidas"""
        # Obtener facturas vencidas del cliente ordenadas por fecha de vencimiento
        overdue_invoices = Invoice.query.filter(
            Invoice.customer_id == payment.customer_id,
            Invoice.balance_amount > 0,
            Invoice.due_date < date.today()
        ).order_by(Invoice.due_date.asc()).all()
        
        for invoice in overdue_invoices:
            if remaining_amount <= 0:
                break
            
            allocation_amount = min(remaining_amount, invoice.balance_amount)
            
            allocation_record = PaymentAllocation(
                payment_id=payment.id,
                invoice_id=invoice.id,
                allocated_amount=allocation_amount
            )
            
            db.session.add(allocation_record)
            
            # Actualizar factura
            invoice.paid_amount += allocation_amount
            invoice.calculate_balance()
            
            remaining_amount -= allocation_amount
    
    def get_payment(self, payment_id: int) -> Optional[Payment]:
        """Obtener pago por ID"""
        return Payment.query.get(payment_id)
    
    def get_payments_by_customer(self, customer_id: int) -> List[Payment]:
        """Obtener pagos por cliente"""
        return Payment.query.filter_by(customer_id=customer_id).order_by(Payment.payment_date.desc()).all()
    
    def get_payments_by_invoice(self, invoice_id: int) -> List[Payment]:
        """Obtener pagos por factura"""
        return Payment.query.join(PaymentAllocation).filter(
            PaymentAllocation.invoice_id == invoice_id
        ).order_by(Payment.payment_date.desc()).all()
    
    # ==================== REPORTES ====================
    
    def get_aging_report(self, customer_id: int = None) -> Dict[str, Any]:
        """Obtener reporte de antigüedad de cartera"""
        query = Invoice.query.filter(Invoice.balance_amount > 0)
        
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        invoices = query.all()
        today = date.today()
        
        aging_buckets = {
            'current': 0,      # 0-30 días
            '31_60': 0,        # 31-60 días
            '61_90': 0,        # 61-90 días
            'over_90': 0       # Más de 90 días
        }
        
        for invoice in invoices:
            days_overdue = (today - invoice.due_date).days
            
            if days_overdue <= 30:
                aging_buckets['current'] += float(invoice.balance_amount)
            elif days_overdue <= 60:
                aging_buckets['31_60'] += float(invoice.balance_amount)
            elif days_overdue <= 90:
                aging_buckets['61_90'] += float(invoice.balance_amount)
            else:
                aging_buckets['over_90'] += float(invoice.balance_amount)
        
        return {
            'aging_buckets': aging_buckets,
            'total_outstanding': sum(aging_buckets.values()),
            'total_invoices': len(invoices)
        }
    
    def get_customer_statement(self, customer_id: int, start_date: date = None, end_date: date = None) -> Dict[str, Any]:
        """Obtener estado de cuenta del cliente"""
        customer = self.get_customer(customer_id)
        if not customer:
            raise ValidationError("Cliente no encontrado")
        
        # Obtener facturas
        invoices_query = Invoice.query.filter_by(customer_id=customer_id)
        if start_date:
            invoices_query = invoices_query.filter(Invoice.invoice_date >= start_date)
        if end_date:
            invoices_query = invoices_query.filter(Invoice.invoice_date <= end_date)
        
        invoices = invoices_query.order_by(Invoice.invoice_date.desc()).all()
        
        # Obtener pagos
        payments_query = Payment.query.filter_by(customer_id=customer_id)
        if start_date:
            payments_query = payments_query.filter(Payment.payment_date >= start_date)
        if end_date:
            payments_query = payments_query.filter(Payment.payment_date <= end_date)
        
        payments = payments_query.order_by(Payment.payment_date.desc()).all()
        
        return {
            'customer': customer.to_dict(),
            'invoices': [invoice.to_dict() for invoice in invoices],
            'payments': [payment.to_dict() for payment in payments],
            'summary': self.get_invoices_summary(customer_id)
        }
    
    def get_collection_efficiency(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Obtener eficiencia de cobranza"""
        # Facturas emitidas en el período
        invoices_issued = Invoice.query.filter(
            Invoice.invoice_date >= start_date,
            Invoice.invoice_date <= end_date
        ).all()
        
        total_issued = sum(float(inv.total_amount) for inv in invoices_issued)
        total_collected = sum(float(inv.paid_amount) for inv in invoices_issued)
        
        # Facturas vencidas
        overdue_invoices = [inv for inv in invoices_issued if inv.is_overdue]
        overdue_amount = sum(float(inv.balance_amount) for inv in overdue_invoices)
        
        # Calcular métricas
        collection_rate = (total_collected / total_issued * 100) if total_issued > 0 else 0
        overdue_rate = (overdue_amount / total_issued * 100) if total_issued > 0 else 0
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_issued': total_issued,
            'total_collected': total_collected,
            'outstanding_amount': total_issued - total_collected,
            'overdue_amount': overdue_amount,
            'collection_rate': collection_rate,
            'overdue_rate': overdue_rate,
            'invoices_count': len(invoices_issued),
            'overdue_count': len(overdue_invoices)
        }
