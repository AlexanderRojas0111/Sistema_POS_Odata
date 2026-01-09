"""
Inventory Service - Sistema POS O'Data
=====================================
Servicio de inventario con lógica de negocio enterprise.
"""

from typing import Dict, Any, Optional, List
from decimal import Decimal
from app.repositories.inventory_repository import InventoryRepository
from app.exceptions import ValidationError, BusinessLogicError, NotFoundError
from app.models.product import Product
from app.models.inventory import InventoryMovement
from app import db

class InventoryService:
    """Servicio de inventario con lógica de negocio enterprise"""
    
    def __init__(self, inventory_repository: InventoryRepository = None):
        # Si no se proporciona repository, crear uno temporal
        if inventory_repository is None:
            from app.container import container
            self.inventory_repository = container.get(InventoryRepository)
        else:
            self.inventory_repository = inventory_repository
    
    def get_inventory_movements(self, page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """Obtener movimientos de inventario"""
        result = self.inventory_repository.get_all(page=page, per_page=per_page, **filters)
        return {
            'movements': [movement.to_dict() for movement in result['items']],
            'pagination': result['pagination']
        }
    
    def get_product_movements(self, product_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener movimientos de un producto específico"""
        result = self.inventory_repository.get_all(page=page, per_page=per_page, product_id=product_id)
        return {
            'movements': [movement.to_dict() for movement in result['items']],
            'pagination': result['pagination']
        }
    
    def get_inventory_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de inventario"""
        return self.inventory_repository.get_inventory_stats()
    
    def get_inventory(self, page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """Obtener inventario con filtros reales"""
        query = Product.query.filter(Product.is_active.is_(True))

        store_id = filters.get('store_id')
        low_stock_only = filters.get('low_stock_only')

        # Filtros básicos
        if low_stock_only:
            query = query.filter(Product.stock <= Product.min_stock)

        # Paginación segura
        pagination = query.order_by(Product.category, Product.name).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        products = [product.to_dict() for product in pagination.items]

        return {
            'inventory': products,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            },
            'filters_applied': {
                'store_id': store_id,
                'low_stock_only': low_stock_only
            }
        }
    
    def get_inventory_summary(self, store_id: Optional[int] = None) -> Dict[str, Any]:
        """Obtener resumen del inventario"""
        products = Product.query.filter(Product.is_active.is_(True)).all()
        total_products = len(products)
        low_stock_count = sum(1 for p in products if p.stock <= (p.min_stock or 5))
        out_of_stock_count = sum(1 for p in products if p.stock <= 0)
        total_stock_units = sum(p.stock for p in products)
        total_value = sum(Decimal(str(p.price)) * p.stock for p in products)

        return {
            'total_products': total_products,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_stock_units': total_stock_units,
            'total_value': float(total_value),
            'store_id': store_id
        }
    
    def get_low_stock_products(self, store_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener productos con stock bajo"""
        products = Product.query.filter(Product.is_active.is_(True)).all()
        low_stock_products = [p for p in products if p.stock <= (p.min_stock or 5)]
        return [p.to_dict() for p in low_stock_products]
    
    def adjust_inventory(self, product_id: int, quantity: int, reason: str, store_id: Optional[int] = None) -> Dict[str, Any]:
        """Ajustar inventario de un producto"""
        product = Product.query.get(product_id)
        if not product:
            raise NotFoundError(f"Product {product_id} not found")

        old_stock = product.stock
        new_stock = old_stock + quantity

        # Evitar stocks negativos no deseados
        if new_stock < 0:
            raise BusinessLogicError("Resultado de stock negativo no permitido", context={
                'product_id': product_id,
                'quantity': quantity,
                'current_stock': old_stock
            })

        product.stock = new_stock

        movement = InventoryMovement(
            product_id=product_id,
            movement_type='adjustment',
            quantity=quantity,
            reason=reason,
            reference_type='manual_adjustment',
            previous_stock=old_stock,
            new_stock=new_stock
        )

        db.session.add(movement)
        db.session.commit()

        return {
            'product': product.to_dict(),
            'movement': movement.to_dict(),
            'store_id': store_id
        }