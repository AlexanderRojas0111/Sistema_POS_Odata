"""
Servicio especializado para gestión de stock
Responsabilidad única: Controlar disponibilidad y reservas de stock
"""

from typing import Dict, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.product import Product
from app.core.database import db
import logging

logger = logging.getLogger(__name__)

class StockService:
    """
    Servicio para gestión de stock de productos
    Maneja disponibilidad, reservas y actualizaciones de stock
    """
    
    def __init__(self):
        self._stock_locks = {}  # En producción, usar Redis para locks distribuidos
    
    def get_available_stock(self, product_id: int) -> Decimal:
        """
        Obtener stock disponible de un producto
        
        Args:
            product_id: ID del producto
            
        Returns:
            Decimal: Cantidad disponible en stock
        """
        product = db.session.query(Product).get(product_id)
        if not product:
            return Decimal('0')
        
        return Decimal(str(product.stock))
    
    def is_stock_available(self, product_id: int, quantity: Decimal) -> bool:
        """
        Verificar si hay stock suficiente para una cantidad solicitada
        
        Args:
            product_id: ID del producto
            quantity: Cantidad solicitada
            
        Returns:
            bool: True si hay stock suficiente
        """
        available = self.get_available_stock(product_id)
        return available >= quantity
    
    def reserve_stock(self, product_id: int, quantity: Decimal) -> bool:
        """
        Reservar stock para una venta (reducir stock disponible)
        
        Args:
            product_id: ID del producto
            quantity: Cantidad a reservar
            
        Returns:
            bool: True si la reserva fue exitosa
            
        Raises:
            RuntimeError: Si no hay stock suficiente
        """
        try:
            # En producción, implementar lock distribuido
            lock_key = f"stock_lock_{product_id}"
            
            product = db.session.query(Product).filter(
                Product.id == product_id
            ).with_for_update().first()  # Pessimistic lock
            
            if not product:
                raise ValueError(f"Producto no encontrado: {product_id}")
            
            current_stock = Decimal(str(product.stock))
            
            if current_stock < quantity:
                raise RuntimeError(
                    f"Stock insuficiente para producto {product.name}. "
                    f"Disponible: {current_stock}, Solicitado: {quantity}"
                )
            
            # Reducir stock
            new_stock = current_stock - quantity
            product.stock = float(new_stock)
            
            logger.info(
                f"Stock reservado para producto {product.name}: "
                f"Cantidad: {quantity}, Stock anterior: {current_stock}, "
                f"Stock nuevo: {new_stock}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error reservando stock: {str(e)}")
            raise
    
    def restore_stock(self, product_id: int, quantity: Decimal) -> bool:
        """
        Restaurar stock (para devoluciones o cancelaciones)
        
        Args:
            product_id: ID del producto
            quantity: Cantidad a restaurar
            
        Returns:
            bool: True si la restauración fue exitosa
        """
        try:
            product = db.session.query(Product).filter(
                Product.id == product_id
            ).with_for_update().first()
            
            if not product:
                raise ValueError(f"Producto no encontrado: {product_id}")
            
            current_stock = Decimal(str(product.stock))
            new_stock = current_stock + quantity
            product.stock = float(new_stock)
            
            logger.info(
                f"Stock restaurado para producto {product.name}: "
                f"Cantidad: {quantity}, Stock anterior: {current_stock}, "
                f"Stock nuevo: {new_stock}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error restaurando stock: {str(e)}")
            raise
    
    def adjust_stock(self, product_id: int, new_quantity: Decimal, reason: str = "manual_adjustment") -> bool:
        """
        Ajustar stock manualmente (para inventarios físicos)
        
        Args:
            product_id: ID del producto
            new_quantity: Nueva cantidad de stock
            reason: Razón del ajuste
            
        Returns:
            bool: True si el ajuste fue exitoso
        """
        try:
            product = db.session.query(Product).filter(
                Product.id == product_id
            ).with_for_update().first()
            
            if not product:
                raise ValueError(f"Producto no encontrado: {product_id}")
            
            old_stock = Decimal(str(product.stock))
            product.stock = float(new_quantity)
            
            logger.info(
                f"Stock ajustado para producto {product.name}: "
                f"Stock anterior: {old_stock}, Stock nuevo: {new_quantity}, "
                f"Razón: {reason}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error ajustando stock: {str(e)}")
            raise
    
    def get_low_stock_products(self, threshold: Decimal = Decimal('10')) -> list:
        """
        Obtener productos con stock bajo
        
        Args:
            threshold: Umbral de stock bajo
            
        Returns:
            list: Lista de productos con stock bajo
        """
        products = db.session.query(Product).filter(
            Product.stock <= float(threshold)
        ).all()
        
        return [
            {
                'id': product.id,
                'name': product.name,
                'code': product.code,
                'current_stock': Decimal(str(product.stock)),
                'threshold': threshold,
                'status': 'critical' if Decimal(str(product.stock)) == 0 else 'low'
            }
            for product in products
        ]
    
    def get_stock_movements_summary(self, product_id: int, days: int = 30) -> Dict:
        """
        Obtener resumen de movimientos de stock para un producto
        
        Args:
            product_id: ID del producto
            days: Días hacia atrás para el análisis
            
        Returns:
            Dict: Resumen de movimientos
        """
        from datetime import datetime, timedelta
        from app.models.inventory import Inventory
        
        start_date = datetime.now() - timedelta(days=days)
        
        movements = db.session.query(Inventory).filter(
            and_(
                Inventory.product_id == product_id,
                Inventory.created_at >= start_date
            )
        ).all()
        
        summary = {
            'product_id': product_id,
            'period_days': days,
            'total_movements': len(movements),
            'movements_by_type': {},
            'net_change': Decimal('0')
        }
        
        for movement in movements:
            movement_type = movement.movement_type
            quantity = Decimal(str(movement.quantity))
            
            # Contar por tipo
            if movement_type not in summary['movements_by_type']:
                summary['movements_by_type'][movement_type] = {
                    'count': 0,
                    'total_quantity': Decimal('0')
                }
            
            summary['movements_by_type'][movement_type]['count'] += 1
            summary['movements_by_type'][movement_type]['total_quantity'] += quantity
            
            # Calcular cambio neto (entradas positivas, salidas negativas)
            if movement_type.lower() in ['compra', 'devolucion', 'ajuste-positivo']:
                summary['net_change'] += quantity
            elif movement_type.lower() in ['venta', 'ajuste-negativo']:
                summary['net_change'] -= quantity
        
        return summary
    
    def validate_stock_consistency(self) -> Dict:
        """
        Validar consistencia entre stock registrado y movimientos de inventario
        
        Returns:
            Dict: Reporte de inconsistencias
        """
        from app.models.inventory import Inventory
        
        inconsistencies = []
        
        # Obtener todos los productos con movimientos
        products_with_movements = db.session.query(Product.id).join(Inventory).distinct().all()
        
        for (product_id,) in products_with_movements:
            # Calcular stock teórico basado en movimientos
            movements = db.session.query(Inventory).filter(
                Inventory.product_id == product_id
            ).order_by(Inventory.created_at).all()
            
            theoretical_stock = Decimal('0')
            for movement in movements:
                quantity = Decimal(str(movement.quantity))
                movement_type = movement.movement_type.lower()
                
                if movement_type in ['compra', 'devolucion', 'ajuste-positivo']:
                    theoretical_stock += quantity
                elif movement_type in ['venta', 'ajuste-negativo']:
                    theoretical_stock -= quantity
            
            # Comparar con stock actual
            product = db.session.query(Product).get(product_id)
            actual_stock = Decimal(str(product.stock))
            
            if abs(theoretical_stock - actual_stock) > Decimal('0.01'):
                inconsistencies.append({
                    'product_id': product_id,
                    'product_name': product.name,
                    'actual_stock': actual_stock,
                    'theoretical_stock': theoretical_stock,
                    'difference': actual_stock - theoretical_stock
                })
        
        return {
            'total_products_checked': len(products_with_movements),
            'inconsistencies_found': len(inconsistencies),
            'inconsistencies': inconsistencies
        }
