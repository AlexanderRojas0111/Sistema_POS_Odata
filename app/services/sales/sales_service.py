"""
Servicio de ventas refactorizado siguiendo principios SOLID
Separa las responsabilidades de gestión de ventas, stock e inventario
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.sale import Sale, SaleItem, SaleStatus, PaymentMethod
from app.models.product import Product
from app.models.inventory import Inventory
from app.core.database import db
from app.services.inventory.stock_service import StockService
from app.services.inventory.inventory_service import InventoryService
from app.schemas import SaleCreate, SaleResponseSchema
import logging

logger = logging.getLogger(__name__)

class SalesService:
    """
    Servicio principal para gestión de ventas
    Responsabilidad única: Crear, actualizar y consultar ventas
    """
    
    def __init__(self, stock_service: StockService, inventory_service: InventoryService):
        self.stock_service = stock_service
        self.inventory_service = inventory_service
    
    def create_sale(self, sale_data: Dict[str, Any], user_id: int) -> Sale:
        """
        Crear una nueva venta con validaciones completas
        
        Args:
            sale_data: Datos de la venta incluyendo items
            user_id: ID del usuario que realiza la venta
            
        Returns:
            Sale: Venta creada
            
        Raises:
            ValueError: Si los datos son inválidos
            RuntimeError: Si hay problemas de stock
        """
        try:
            with db.session.begin():  # Transacción atómica
                # 1. Validar datos de entrada
                self._validate_sale_data(sale_data)
                
                # 2. Verificar disponibilidad de stock para todos los items
                self._validate_stock_availability(sale_data['items'])
                
                # 3. Crear la venta principal
                sale = self._create_sale_record(sale_data, user_id)
                
                # 4. Crear los items de venta
                total_calculated = Decimal('0')
                for item_data in sale_data['items']:
                    sale_item = self._create_sale_item(sale, item_data)
                    total_calculated += sale_item.quantity * sale_item.unit_price * (1 - sale_item.discount)
                
                # 5. Validar que el total calculado coincida con el enviado
                if abs(total_calculated - Decimal(str(sale_data['total_amount']))) > Decimal('0.01'):
                    raise ValueError(f"Total calculado ({total_calculated}) no coincide con el enviado ({sale_data['total_amount']})")
                
                sale.total_amount = float(total_calculated)
                
                # 6. Reservar stock para todos los productos
                self._reserve_stock_for_sale(sale)
                
                # 7. Registrar movimientos de inventario
                self._register_inventory_movements(sale, user_id)
                
                # 8. Marcar venta como completada
                sale.status = SaleStatus.COMPLETED
                
                db.session.add(sale)
                db.session.flush()  # Para obtener el ID
                
                logger.info(f"Venta creada exitosamente: ID {sale.id}, Total: ${sale.total_amount}")
                return sale
                
        except Exception as e:
            logger.error(f"Error creando venta: {str(e)}")
            db.session.rollback()
            raise
    
    def _validate_sale_data(self, sale_data: Dict[str, Any]) -> None:
        """Validar estructura y datos de la venta"""
        required_fields = ['items', 'payment_method', 'total_amount']
        for field in required_fields:
            if field not in sale_data:
                raise ValueError(f"Campo requerido faltante: {field}")
        
        if not sale_data['items']:
            raise ValueError("La venta debe tener al menos un item")
        
        if Decimal(str(sale_data['total_amount'])) <= 0:
            raise ValueError("El total de la venta debe ser mayor a 0")
        
        # Validar método de pago
        try:
            PaymentMethod(sale_data['payment_method'])
        except ValueError:
            raise ValueError(f"Método de pago inválido: {sale_data['payment_method']}")
    
    def _validate_stock_availability(self, items: List[Dict[str, Any]]) -> None:
        """Validar que hay stock suficiente para todos los productos"""
        for item in items:
            product_id = item['product_id']
            quantity = Decimal(str(item['quantity']))
            
            if not self.stock_service.is_stock_available(product_id, quantity):
                product = db.session.query(Product).get(product_id)
                product_name = product.name if product else f"ID {product_id}"
                raise RuntimeError(f"Stock insuficiente para {product_name}. Solicitado: {quantity}, Disponible: {self.stock_service.get_available_stock(product_id)}")
    
    def _create_sale_record(self, sale_data: Dict[str, Any], user_id: int) -> Sale:
        """Crear el registro principal de venta"""
        sale = Sale(
            invoice_number=self._generate_invoice_number(),
            customer_id=sale_data.get('customer_id'),
            user_id=user_id,
            payment_method=PaymentMethod(sale_data['payment_method']),
            status=SaleStatus.PENDING,
            sale_metadata=sale_data.get('metadata', {})
        )
        return sale
    
    def _create_sale_item(self, sale: Sale, item_data: Dict[str, Any]) -> SaleItem:
        """Crear un item de venta individual"""
        product = db.session.query(Product).get(item_data['product_id'])
        if not product:
            raise ValueError(f"Producto no encontrado: {item_data['product_id']}")
        
        sale_item = SaleItem(
            sale=sale,
            product_id=product.id,
            quantity=Decimal(str(item_data['quantity'])),
            unit_price=Decimal(str(item_data.get('unit_price', product.price))),
            discount=Decimal(str(item_data.get('discount', 0)))
        )
        
        sale.items.append(sale_item)
        return sale_item
    
    def _reserve_stock_for_sale(self, sale: Sale) -> None:
        """Reservar stock para todos los items de la venta"""
        for item in sale.items:
            self.stock_service.reserve_stock(item.product_id, item.quantity)
    
    def _register_inventory_movements(self, sale: Sale, user_id: int) -> None:
        """Registrar movimientos de inventario para la venta"""
        for item in sale.items:
            self.inventory_service.record_movement(
                product_id=item.product_id,
                quantity=item.quantity,
                movement_type='venta',
                user_id=user_id,
                reference_type='sale',
                reference_id=sale.id
            )
    
    def _generate_invoice_number(self) -> str:
        """Generar número de factura único"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # En producción, usar un sistema más robusto con secuencias
        return f"TICKET-{timestamp}"
    
    def get_sale(self, sale_id: int) -> Optional[Sale]:
        """Obtener una venta por ID"""
        return db.session.query(Sale).filter(Sale.id == sale_id).first()
    
    def get_daily_sales(self, date: datetime = None) -> List[Sale]:
        """Obtener ventas de un día específico"""
        if date is None:
            date = datetime.now().date()
        
        start_date = datetime.combine(date, datetime.min.time())
        end_date = datetime.combine(date, datetime.max.time())
        
        return db.session.query(Sale).filter(
            and_(
                Sale.created_at >= start_date,
                Sale.created_at <= end_date,
                Sale.status == SaleStatus.COMPLETED
            )
        ).all()
    
    def get_sales_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generar reporte de ventas para un período"""
        sales = db.session.query(Sale).filter(
            and_(
                Sale.created_at >= start_date,
                Sale.created_at <= end_date,
                Sale.status == SaleStatus.COMPLETED
            )
        ).all()
        
        total_amount = sum(sale.total_amount for sale in sales)
        total_transactions = len(sales)
        total_items = sum(len(sale.items) for sale in sales)
        
        # Agrupar por método de pago
        payment_methods = {}
        for sale in sales:
            method = sale.payment_method.value
            payment_methods[method] = payment_methods.get(method, 0) + sale.total_amount
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_amount': total_amount,
                'total_transactions': total_transactions,
                'total_items': total_items,
                'average_ticket': total_amount / total_transactions if total_transactions > 0 else 0
            },
            'payment_methods': payment_methods,
            'sales': [SaleResponse.from_orm(sale).dict() for sale in sales]
        }

class SaleRefundService:
    """
    Servicio separado para manejo de devoluciones
    Responsabilidad única: Procesar reembolsos y devoluciones
    """
    
    def __init__(self, stock_service: StockService, inventory_service: InventoryService):
        self.stock_service = stock_service
        self.inventory_service = inventory_service
    
    def process_refund(self, sale_id: int, refund_items: List[Dict[str, Any]], user_id: int) -> Sale:
        """
        Procesar devolución parcial o total de una venta
        
        Args:
            sale_id: ID de la venta original
            refund_items: Items a devolver con cantidades
            user_id: ID del usuario que procesa la devolución
        """
        try:
            with db.session.begin():
                # 1. Obtener venta original
                original_sale = db.session.query(Sale).get(sale_id)
                if not original_sale:
                    raise ValueError(f"Venta no encontrada: {sale_id}")
                
                if original_sale.status != SaleStatus.COMPLETED:
                    raise ValueError("Solo se pueden devolver ventas completadas")
                
                # 2. Validar items a devolver
                self._validate_refund_items(original_sale, refund_items)
                
                # 3. Crear registro de devolución
                refund_sale = self._create_refund_record(original_sale, user_id)
                
                # 4. Procesar cada item de devolución
                total_refund = Decimal('0')
                for refund_item in refund_items:
                    refund_amount = self._process_refund_item(
                        refund_sale, original_sale, refund_item, user_id
                    )
                    total_refund += refund_amount
                
                refund_sale.total_amount = -float(total_refund)  # Negativo para devolución
                refund_sale.status = SaleStatus.COMPLETED
                
                db.session.add(refund_sale)
                
                logger.info(f"Devolución procesada: Sale ID {sale_id}, Refund Amount: ${total_refund}")
                return refund_sale
                
        except Exception as e:
            logger.error(f"Error procesando devolución: {str(e)}")
            db.session.rollback()
            raise
    
    def _validate_refund_items(self, original_sale: Sale, refund_items: List[Dict[str, Any]]) -> None:
        """Validar que los items a devolver son válidos"""
        for refund_item in refund_items:
            product_id = refund_item['product_id']
            refund_quantity = Decimal(str(refund_item['quantity']))
            
            # Buscar el item original
            original_item = next(
                (item for item in original_sale.items if item.product_id == product_id),
                None
            )
            
            if not original_item:
                raise ValueError(f"Producto {product_id} no está en la venta original")
            
            if refund_quantity > original_item.quantity:
                raise ValueError(f"Cantidad a devolver ({refund_quantity}) mayor que la vendida ({original_item.quantity})")
    
    def _create_refund_record(self, original_sale: Sale, user_id: int) -> Sale:
        """Crear registro de devolución"""
        refund_sale = Sale(
            invoice_number=f"REFUND-{original_sale.invoice_number}",
            customer_id=original_sale.customer_id,
            user_id=user_id,
            payment_method=original_sale.payment_method,
            status=SaleStatus.PENDING,
            sale_metadata={
                'refund_of': original_sale.id,
                'original_invoice': original_sale.invoice_number
            }
        )
        return refund_sale
    
    def _process_refund_item(self, refund_sale: Sale, original_sale: Sale, refund_item: Dict[str, Any], user_id: int) -> Decimal:
        """Procesar devolución de un item individual"""
        product_id = refund_item['product_id']
        refund_quantity = Decimal(str(refund_item['quantity']))
        
        # Buscar item original para obtener precio
        original_item = next(
            item for item in original_sale.items 
            if item.product_id == product_id
        )
        
        # Crear item de devolución
        refund_sale_item = SaleItem(
            sale=refund_sale,
            product_id=product_id,
            quantity=-refund_quantity,  # Negativo para devolución
            unit_price=original_item.unit_price,
            discount=original_item.discount
        )
        
        refund_sale.items.append(refund_sale_item)
        
        # Restaurar stock
        self.stock_service.restore_stock(product_id, refund_quantity)
        
        # Registrar movimiento de inventario
        self.inventory_service.record_movement(
            product_id=product_id,
            quantity=refund_quantity,
            movement_type='devolucion',
            user_id=user_id,
            reference_type='refund',
            reference_id=refund_sale.id
        )
        
        # Calcular monto de devolución
        return refund_quantity * original_item.unit_price * (1 - original_item.discount)
