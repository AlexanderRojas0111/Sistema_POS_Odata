"""
Product Repository - Sistema POS O'Data
======================================
Repository específico para productos con operaciones especializadas.
"""

from typing import Optional, List, Dict, Any
from app import db
from app.repositories.base_repository import BaseRepository
from app.models.product import Product
from app.exceptions import ValidationError, NotFoundError

class ProductRepository(BaseRepository[Product]):
    """Repository para productos con operaciones especializadas"""
    
    def __init__(self):
        super().__init__(Product)
    
    def get_by_sku(self, sku: str) -> Optional[Product]:
        """Obtener producto por SKU"""
        return Product.query.filter_by(sku=sku).first()
    
    def get_by_barcode(self, barcode: str) -> Optional[Product]:
        """Obtener producto por código de barras"""
        return Product.query.filter_by(barcode=barcode).first()
    
    def get_by_sku_or_404(self, sku: str) -> Product:
        """Obtener producto por SKU o lanzar 404"""
        product = self.get_by_sku(sku)
        if not product:
            raise NotFoundError("Product", sku)
        return product
    
    def create_product(self, name: str, sku: str, price: float, **kwargs) -> Product:
        """Crear producto con validaciones específicas"""
        # Validar unicidad de SKU
        if self.get_by_sku(sku):
            raise ValidationError(f"SKU '{sku}' already exists", field="sku")
        
        # Validar precio positivo
        if price <= 0:
            raise ValidationError("Price must be greater than 0", field="price")
        
        # Validar nombre no vacío
        if not name or len(name.strip()) == 0:
            raise ValidationError("Product name is required", field="name")
        
        return self.create(
            name=name.strip(),
            sku=sku.upper().strip(),
            price=price,
            **kwargs
        )
    
    def get_active_products(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener productos activos"""
        return self.get_all(page=page, per_page=per_page, is_active=True)
    
    def get_by_category(self, category: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener productos por categoría"""
        return self.get_all(page=page, per_page=per_page, category=category, is_active=True)
    
    def get_low_stock_products(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener productos con stock bajo"""
        query = Product.query.filter(
            Product.stock <= Product.min_stock,
            Product.is_active == True
        )
        
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'items': pagination.items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    
    def get_out_of_stock_products(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener productos agotados"""
        return self.get_all(page=page, per_page=per_page, stock=0, is_active=True)
    
    def search_products(self, search_term: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Buscar productos en múltiples campos"""
        search_fields = ['name', 'description', 'sku', 'barcode', 'category', 'brand']
        return self.search(search_term, search_fields, page, per_page)
    
    def update_stock(self, product_id: int, new_stock: int, reason: str = "manual_adjustment") -> Product:
        """Actualizar stock del producto"""
        product = self.get_by_id_or_404(product_id)
        
        if new_stock < 0:
            raise ValidationError("Stock cannot be negative", field="stock")
        
        old_stock = product.stock
        product.stock = new_stock
        
        # Crear movimiento de inventario
        from app.models.inventory import InventoryMovement
        movement = InventoryMovement(
            product_id=product_id,
            movement_type='adjustment',
            quantity=new_stock - old_stock,
            reason=reason,
            previous_stock=old_stock,
            new_stock=new_stock
        )
        
        from app import db
        db.session.add(movement)
        db.session.commit()
        
        return product
    
    def adjust_stock(self, product_id: int, quantity_change: int, reason: str = "adjustment") -> Product:
        """Ajustar stock del producto (puede ser positivo o negativo)"""
        product = self.get_by_id_or_404(product_id)
        
        new_stock = product.stock + quantity_change
        if new_stock < 0:
            raise ValidationError("Insufficient stock for this adjustment", field="stock")
        
        return self.update_stock(product_id, new_stock, reason)
    
    def get_top_selling_products(self, limit: int = 10) -> List[Product]:
        """Obtener productos más vendidos"""
        from app.models.sale import SaleItem
        from sqlalchemy import func, desc
        
        top_products = db.session.query(
            Product,
            func.sum(SaleItem.quantity).label('total_sold')
        ).join(
            SaleItem, Product.id == SaleItem.product_id
        ).group_by(
            Product.id
        ).order_by(
            desc('total_sold')
        ).limit(limit).all()
        
        return [product for product, _ in top_products]
    
    def get_products_needing_reorder(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener productos que necesitan reorden"""
        query = Product.query.filter(
            Product.stock <= Product.reorder_point,
            Product.is_active == True
        )
        
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'items': pagination.items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    
    def get_product_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de productos"""
        total_products = self.count()
        active_products = self.count(is_active=True)
        low_stock_count = self.count(is_active=True) - self.count(stock=0, is_active=True)
        out_of_stock_count = self.count(stock=0, is_active=True)
        
        return {
            'total_products': total_products,
            'active_products': active_products,
            'inactive_products': total_products - active_products,
            'low_stock_products': low_stock_count,
            'out_of_stock_products': out_of_stock_count
        }
