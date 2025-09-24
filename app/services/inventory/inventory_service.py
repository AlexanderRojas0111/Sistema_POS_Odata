"""
Servicio para gestión de inventario y trazabilidad
Responsabilidad única: Registrar y consultar movimientos de inventario
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy import and_, desc

from app.models.inventory import Inventory
from app.models.product import Product
from app.core.database import db
import logging

logger = logging.getLogger(__name__)

class InventoryService:
    """
    Servicio para gestión de inventario y trazabilidad de movimientos
    """
    
    def record_movement(self, 
                       product_id: int, 
                       quantity: Decimal, 
                       movement_type: str,
                       user_id: int,
                       reference_type: str = None,
                       reference_id: int = None,
                       notes: str = None) -> Inventory:
        """
        Registrar un movimiento de inventario
        
        Args:
            product_id: ID del producto
            quantity: Cantidad del movimiento
            movement_type: Tipo de movimiento (compra, venta, ajuste, etc.)
            user_id: ID del usuario que registra el movimiento
            reference_type: Tipo de referencia (sale, purchase, adjustment)
            reference_id: ID de la referencia
            notes: Notas adicionales
            
        Returns:
            Inventory: Registro de inventario creado
        """
        try:
            # Validar que el producto existe
            product = db.session.query(Product).get(product_id)
            if not product:
                raise ValueError(f"Producto no encontrado: {product_id}")
            
            # Crear registro de inventario
            inventory_record = Inventory(
                product_id=product_id,
                quantity=float(quantity),
                movement_type=movement_type,
                user_id=user_id,
                reference_type=reference_type,
                reference_id=reference_id,
                notes=notes
            )
            
            db.session.add(inventory_record)
            db.session.flush()  # Para obtener el ID
            
            logger.info(
                f"Movimiento de inventario registrado: "
                f"Producto: {product.name}, Tipo: {movement_type}, "
                f"Cantidad: {quantity}, Usuario: {user_id}"
            )
            
            return inventory_record
            
        except Exception as e:
            logger.error(f"Error registrando movimiento de inventario: {str(e)}")
            raise
    
    def get_product_movements(self, 
                             product_id: int, 
                             start_date: datetime = None,
                             end_date: datetime = None,
                             movement_type: str = None,
                             limit: int = 100) -> List[Inventory]:
        """
        Obtener movimientos de inventario para un producto
        
        Args:
            product_id: ID del producto
            start_date: Fecha de inicio del filtro
            end_date: Fecha de fin del filtro
            movement_type: Tipo de movimiento a filtrar
            limit: Límite de registros a retornar
            
        Returns:
            List[Inventory]: Lista de movimientos
        """
        query = db.session.query(Inventory).filter(
            Inventory.product_id == product_id
        )
        
        if start_date:
            query = query.filter(Inventory.created_at >= start_date)
        
        if end_date:
            query = query.filter(Inventory.created_at <= end_date)
        
        if movement_type:
            query = query.filter(Inventory.movement_type == movement_type)
        
        return query.order_by(desc(Inventory.created_at)).limit(limit).all()
    
    def get_movements_by_user(self, 
                             user_id: int,
                             start_date: datetime = None,
                             end_date: datetime = None,
                             limit: int = 100) -> List[Inventory]:
        """
        Obtener movimientos de inventario realizados por un usuario
        
        Args:
            user_id: ID del usuario
            start_date: Fecha de inicio del filtro
            end_date: Fecha de fin del filtro
            limit: Límite de registros a retornar
            
        Returns:
            List[Inventory]: Lista de movimientos
        """
        query = db.session.query(Inventory).filter(
            Inventory.user_id == user_id
        )
        
        if start_date:
            query = query.filter(Inventory.created_at >= start_date)
        
        if end_date:
            query = query.filter(Inventory.created_at <= end_date)
        
        return query.order_by(desc(Inventory.created_at)).limit(limit).all()
    
    def get_movements_summary(self, 
                             start_date: datetime = None,
                             end_date: datetime = None) -> Dict[str, Any]:
        """
        Obtener resumen de movimientos de inventario
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Dict: Resumen de movimientos
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        
        if not end_date:
            end_date = datetime.now()
        
        movements = db.session.query(Inventory).filter(
            and_(
                Inventory.created_at >= start_date,
                Inventory.created_at <= end_date
            )
        ).all()
        
        summary = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_movements': len(movements),
            'movements_by_type': {},
            'movements_by_user': {},
            'products_affected': set(),
            'total_value_in': Decimal('0'),
            'total_value_out': Decimal('0')
        }
        
        for movement in movements:
            movement_type = movement.movement_type
            user_id = movement.user_id
            product_id = movement.product_id
            quantity = Decimal(str(movement.quantity))
            
            # Contar por tipo
            if movement_type not in summary['movements_by_type']:
                summary['movements_by_type'][movement_type] = 0
            summary['movements_by_type'][movement_type] += 1
            
            # Contar por usuario
            if user_id not in summary['movements_by_user']:
                summary['movements_by_user'][user_id] = 0
            summary['movements_by_user'][user_id] += 1
            
            # Productos afectados
            summary['products_affected'].add(product_id)
            
            # Calcular valores (necesitaríamos precio del producto en el momento)
            # Por ahora solo contamos cantidades
        
        summary['products_affected'] = len(summary['products_affected'])
        
        return summary
    
    def audit_inventory_changes(self, 
                               product_id: int = None,
                               days_back: int = 7) -> Dict[str, Any]:
        """
        Auditar cambios de inventario para detectar anomalías
        
        Args:
            product_id: ID del producto específico (None para todos)
            days_back: Días hacia atrás para el análisis
            
        Returns:
            Dict: Reporte de auditoría
        """
        start_date = datetime.now() - timedelta(days=days_back)
        
        query = db.session.query(Inventory).filter(
            Inventory.created_at >= start_date
        )
        
        if product_id:
            query = query.filter(Inventory.product_id == product_id)
        
        movements = query.order_by(Inventory.created_at).all()
        
        audit_report = {
            'audit_period': {
                'start_date': start_date.isoformat(),
                'end_date': datetime.now().isoformat(),
                'days_analyzed': days_back
            },
            'total_movements': len(movements),
            'anomalies': [],
            'statistics': {
                'large_movements': [],  # Movimientos inusualmente grandes
                'frequent_adjustments': [],  # Productos con muchos ajustes
                'negative_stock_risks': []  # Productos que podrían quedar en negativo
            }
        }
        
        # Analizar movimientos por producto
        product_movements = {}
        for movement in movements:
            product_id = movement.product_id
            if product_id not in product_movements:
                product_movements[product_id] = []
            product_movements[product_id].append(movement)
        
        for product_id, product_mvmts in product_movements.items():
            # Detectar movimientos grandes (más del 50% del stock promedio)
            quantities = [abs(float(m.quantity)) for m in product_mvmts]
            if quantities:
                avg_quantity = sum(quantities) / len(quantities)
                for movement in product_mvmts:
                    if abs(float(movement.quantity)) > avg_quantity * 2:
                        audit_report['statistics']['large_movements'].append({
                            'product_id': product_id,
                            'movement_id': movement.id,
                            'quantity': movement.quantity,
                            'type': movement.movement_type,
                            'date': movement.created_at.isoformat(),
                            'user_id': movement.user_id
                        })
            
            # Detectar ajustes frecuentes
            adjustments = [m for m in product_mvmts if 'ajuste' in m.movement_type.lower()]
            if len(adjustments) > 5:  # Más de 5 ajustes en el período
                audit_report['statistics']['frequent_adjustments'].append({
                    'product_id': product_id,
                    'adjustment_count': len(adjustments),
                    'period_days': days_back
                })
        
        return audit_report
    
    def reconcile_inventory(self, 
                           product_id: int,
                           physical_count: Decimal,
                           user_id: int,
                           notes: str = None) -> Dict[str, Any]:
        """
        Reconciliar inventario físico vs sistema
        
        Args:
            product_id: ID del producto
            physical_count: Conteo físico real
            user_id: ID del usuario que realiza la reconciliación
            notes: Notas de la reconciliación
            
        Returns:
            Dict: Resultado de la reconciliación
        """
        try:
            product = db.session.query(Product).get(product_id)
            if not product:
                raise ValueError(f"Producto no encontrado: {product_id}")
            
            system_stock = Decimal(str(product.stock))
            difference = physical_count - system_stock
            
            reconciliation_result = {
                'product_id': product_id,
                'product_name': product.name,
                'system_stock': system_stock,
                'physical_count': physical_count,
                'difference': difference,
                'reconciliation_needed': abs(difference) > Decimal('0.01'),
                'adjustment_made': False
            }
            
            # Si hay diferencia significativa, crear ajuste
            if abs(difference) > Decimal('0.01'):
                adjustment_type = 'ajuste-positivo' if difference > 0 else 'ajuste-negativo'
                
                # Registrar movimiento de ajuste
                self.record_movement(
                    product_id=product_id,
                    quantity=abs(difference),
                    movement_type=adjustment_type,
                    user_id=user_id,
                    reference_type='reconciliation',
                    notes=f"Reconciliación de inventario. {notes or ''}"
                )
                
                # Actualizar stock del producto
                product.stock = float(physical_count)
                
                reconciliation_result['adjustment_made'] = True
                
                logger.info(
                    f"Inventario reconciliado para {product.name}: "
                    f"Sistema: {system_stock}, Físico: {physical_count}, "
                    f"Diferencia: {difference}"
                )
            
            return reconciliation_result
            
        except Exception as e:
            logger.error(f"Error en reconciliación de inventario: {str(e)}")
            raise
    
    def get_inventory_valuation(self, 
                               as_of_date: datetime = None) -> Dict[str, Any]:
        """
        Calcular valuación del inventario
        
        Args:
            as_of_date: Fecha para la valuación (None para actual)
            
        Returns:
            Dict: Valuación del inventario
        """
        if not as_of_date:
            as_of_date = datetime.now()
        
        # Obtener todos los productos con stock
        products = db.session.query(Product).filter(
            Product.stock > 0
        ).all()
        
        valuation = {
            'valuation_date': as_of_date.isoformat(),
            'total_products': len(products),
            'total_units': Decimal('0'),
            'total_value': Decimal('0'),
            'products': []
        }
        
        for product in products:
            stock_quantity = Decimal(str(product.stock))
            unit_value = Decimal(str(product.price))
            total_value = stock_quantity * unit_value
            
            valuation['total_units'] += stock_quantity
            valuation['total_value'] += total_value
            
            valuation['products'].append({
                'id': product.id,
                'name': product.name,
                'code': product.code,
                'stock_quantity': stock_quantity,
                'unit_value': unit_value,
                'total_value': total_value,
                'category': product.category
            })
        
        # Ordenar por valor total descendente
        valuation['products'].sort(key=lambda x: x['total_value'], reverse=True)
        
        return valuation
