"""
Sale Service - Sistema POS O'Data
================================
Servicio de ventas con lógica de negocio enterprise.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
import logging
from app.repositories.sale_repository import SaleRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.exceptions import ValidationError, InsufficientStockError, BusinessLogicError
from app import db

logger = logging.getLogger(__name__)

class SaleService:
    """Servicio de ventas con lógica de negocio enterprise"""
    
    def __init__(
        self, 
        sale_repository: SaleRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository
    ):
        self.sale_repository = sale_repository
        self.product_repository = product_repository
        self.user_repository = user_repository
    
    def create_sale(self, user_id: int, sale_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nueva venta con validaciones enterprise"""
        # Validar usuario
        user = self.user_repository.get_by_id_or_404(user_id)
        if not user.is_active:
            raise ValidationError("User is not active", field="user_id")
        
        # Validar items
        items = sale_data.get('items', [])
        if not items:
            raise ValidationError("Sale must have at least one item", field="items")
        
        # Validar y procesar items
        validated_items = self._validate_and_process_items(items)
        
        # Crear venta
        sale = self.sale_repository.create(
            user_id=user_id,
            items=validated_items,
            customer_id=sale_data.get('customer_id'),
            payment_method=sale_data.get('payment_method', 'cash'),
            payment_reference=sale_data.get('payment_reference'),
            notes=sale_data.get('notes')
        )
        
        # Procesar items y actualizar stock
        self._process_sale_items(sale, validated_items)
        
        # Aplicar impuestos y descuentos si se especifican
        if 'tax_rate' in sale_data:
            sale.apply_tax(sale_data['tax_rate'])
        
        if 'discount_amount' in sale_data:
            sale.apply_discount(sale_data['discount_amount'], sale_data.get('discount_type', 'fixed'))
        
        # Calcular cambio si es pago en efectivo
        if sale.payment_method == 'cash' and 'amount_paid' in sale_data:
            amount_paid = Decimal(str(sale_data['amount_paid']))
            if amount_paid < sale.total_amount:
                raise ValidationError("Amount paid is less than total amount", field="amount_paid")
            sale.change_amount = amount_paid - sale.total_amount
        
        db.session.commit()
        
        # IA: sugerencias de productos relacionados (best-effort)
        sale_dict = sale.to_dict()
        sale_dict['ai_recommendations'] = self._get_ai_recommendations(validated_items)

        # Enviar factura por email si se proporciona email del cliente
        try:
            from app.services.email_service import email_service
            
            if sale_data.get('customer_email'):
                # Preparar datos para la factura
                sale_dict = sale.to_dict()
                
                # Agregar datos del cliente
                sale_dict['customer_email'] = sale_data.get('customer_email')
                sale_dict['customer_name'] = sale_data.get('customer_name', 'Cliente')
                
                # Agregar items con nombres de productos
                sale_dict['items'] = [
                    {
                        'name': item['product_name'],
                        'quantity': item['quantity'],
                        'unit_price': float(item['unit_price']),
                        'total': float(item['quantity'] * item['unit_price'])
                    }
                    for item in validated_items
                ]
                
                # Enviar factura por email
                email_sent = email_service.send_sale_invoice(sale_dict)
                if email_sent:
                    logger.info(f"Factura enviada por email para venta {sale.id}")
                else:
                    logger.warning(f"No se pudo enviar factura por email para venta {sale.id}")
        except Exception as e:
            logger.error(f"Error enviando factura por email: {str(e)}")
            # No fallar la venta si el email falla
        
        return sale_dict
    
    def _validate_and_process_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validar y procesar items de venta"""
        validated_items = []
        
        for item_data in items:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 1)
            unit_price = item_data.get('unit_price')
            
            # Validar producto
            product = self.product_repository.get_by_id_or_404(product_id)
            if not product.is_active:
                raise ValidationError(f"Product {product.name} is not active", field="product_id")
            
            # Validar stock
            if product.stock < quantity:
                raise InsufficientStockError(product_id, quantity, product.stock)
            
            # Usar precio del producto si no se especifica
            if unit_price is None:
                unit_price = float(product.price)
            
            validated_items.append({
                'product_id': product_id,
                'product_name': product.name,
                'quantity': quantity,
                'unit_price': unit_price
            })
        
        return validated_items
    
    def _process_sale_items(self, sale, items: List[Dict[str, Any]]) -> None:
        """Procesar items de venta y actualizar stock"""
        from app.models.sale import SaleItem
        from app.models.inventory import InventoryMovement
        
        for item_data in items:
            product_id = item_data['product_id']
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']
            
            # Crear item de venta
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product_id,
                quantity=quantity,
                unit_price=Decimal(str(unit_price))
            )
            
            db.session.add(sale_item)
            
            # Actualizar stock del producto
            product = self.product_repository.get_by_id(product_id)
            old_stock = product.stock
            product.stock -= quantity
            
            # Crear movimiento de inventario
            movement = InventoryMovement(
                product_id=product_id,
                movement_type='sale',
                quantity=-quantity,  # Negativo para salida
                reason=f'Sale #{sale.id}',
                reference_id=sale.id,
                reference_type='sale',
                previous_stock=old_stock,
                new_stock=product.stock
            )
            
            db.session.add(movement)
    
    def get_sale(self, sale_id: int) -> Dict[str, Any]:
        """Obtener venta por ID"""
        sale = self.sale_repository.get_by_id_or_404(sale_id)
        return sale.to_dict()
    
    def get_sales(self, page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """Obtener ventas con filtros"""
        return self.sale_repository.get_all(page=page, per_page=per_page, **filters)
    
    def get_sales_by_user(self, user_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener ventas por usuario"""
        return self.sale_repository.get_all(page=page, per_page=per_page, user_id=user_id)
    
    def cancel_sale(self, sale_id: int, reason: str = "Cancelled by user") -> Dict[str, Any]:
        """Cancelar venta y revertir stock"""
        sale = self.sale_repository.get_by_id_or_404(sale_id)
        
        if sale.status == 'cancelled':
            raise BusinessLogicError("Sale is already cancelled", operation="cancel_sale")
        
        # Revertir stock para cada item
        for item in sale.items:
            product = self.product_repository.get_by_id(item.product_id)
            product.stock += item.quantity
            
            # Crear movimiento de inventario de reversión
            from app.models.inventory import InventoryMovement
            movement = InventoryMovement(
                product_id=item.product_id,
                movement_type='adjustment',
                quantity=item.quantity,
                reason=f'Sale cancellation - {reason}',
                reference_id=sale.id,
                reference_type='sale_cancellation',
                previous_stock=product.stock - item.quantity,
                new_stock=product.stock
            )
            
            db.session.add(movement)
        
        # Actualizar estado de la venta
        sale.status = 'cancelled'
        sale.notes = f"{sale.notes or ''}\nCancelled: {reason}".strip()
        
        db.session.commit()
        
        return sale.to_dict()

    def update_sale(self, sale_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar metadatos de la venta (estado, notas, método de pago, impuestos/discount)"""
        sale = self.sale_repository.get_by_id_or_404(sale_id)

        # Estado con control de transición
        new_status = updates.get('status')
        if new_status:
            allowed_status = {'completed', 'pending', 'refunded', 'cancelled'}
            if new_status not in allowed_status:
                raise ValidationError(f"Invalid status '{new_status}'", field="status")
            if new_status == 'cancelled' and sale.status != 'cancelled':
                # Reusar lógica de cancelación para stock
                return self.cancel_sale(sale_id, reason=updates.get('reason', 'Updated via API'))
            sale.status = new_status

        if 'notes' in updates:
            sale.notes = updates.get('notes')

        if 'payment_method' in updates:
            sale.payment_method = updates.get('payment_method') or sale.payment_method

        if 'payment_reference' in updates:
            sale.payment_reference = updates.get('payment_reference')

        if 'discount_amount' in updates:
            sale.apply_discount(updates.get('discount_amount', 0))

        if 'tax_rate' in updates:
            sale.apply_tax(updates.get('tax_rate', 0))

        db.session.commit()
        return sale.to_dict()
    
    def get_sales_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Obtener estadísticas de ventas"""
        from sqlalchemy import func, desc
        from app.models.sale import Sale
        
        query = Sale.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        # Estadísticas básicas
        total_sales = query.count()
        total_amount = query.with_entities(func.sum(Sale.total_amount)).scalar() or 0
        
        # Ventas del día
        from datetime import datetime, date
        today = date.today()
        today_sales = query.filter(
            func.date(Sale.created_at) == today
        ).count()
        
        today_amount = query.filter(
            func.date(Sale.created_at) == today
        ).with_entities(func.sum(Sale.total_amount)).scalar() or 0
        
        # Promedio por venta
        avg_sale_amount = float(total_amount / total_sales) if total_sales > 0 else 0
        
        return {
            'total_sales': total_sales,
            'total_amount': float(total_amount),
            'today_sales': today_sales,
            'today_amount': float(today_amount),
            'average_sale_amount': avg_sale_amount
        }

    def _get_ai_recommendations(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Obtener recomendaciones de productos basadas en el primer item (mejor esfuerzo)"""
        try:
            if not items:
                return []
            from app.services.ai_service import AIService

            first_product_id = items[0].get('product_id')
            if not first_product_id:
                return []

            ai_service = AIService()
            return ai_service.get_recommendations(first_product_id, limit=5) or []
        except Exception as e:  # pragma: no cover - IA opcional
            logger.warning(f"AI recommendations unavailable: {e}")
            return []
