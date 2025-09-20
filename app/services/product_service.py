"""
Product Service - Sistema POS O'Data
===================================
Servicio de productos con lógica de negocio enterprise.
"""

from typing import Dict, Any, Optional, List
from app.repositories.product_repository import ProductRepository
from app.exceptions import ValidationError, BusinessLogicError
from app import db

class ProductService:
    """Servicio de productos con lógica de negocio enterprise"""
    
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
    
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nuevo producto"""
        # Validar campos requeridos
        required_fields = ['name', 'sku', 'price']
        for field in required_fields:
            if field not in product_data:
                raise ValueError(f"Field '{field}' is required")
        
        # Extraer campos requeridos y opcionales
        name = product_data['name']
        sku = product_data['sku']
        price = product_data['price']
        
        # Campos opcionales con valores por defecto
        optional_fields = {
            'description': product_data.get('description', ''),
            'category': product_data.get('category', 'Sencillas'),
            'cost': product_data.get('cost', 0.0),
            'stock': product_data.get('stock', 0),
            'min_stock': product_data.get('min_stock', 5),
            'is_active': product_data.get('is_active', True),
            'image_url': product_data.get('image_url', None),
            'barcode': product_data.get('barcode', None),
            'unit': product_data.get('unit', 'unidad'),
            'weight': product_data.get('weight', None),
            'dimensions': product_data.get('dimensions', None),
            'supplier': product_data.get('supplier', None),
            'location': product_data.get('location', None),
            'notes': product_data.get('notes', None)
        }
        
        return self.product_repository.create_product(
            name=name, 
            sku=sku, 
            price=price, 
            **optional_fields
        ).to_dict()
    
    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Obtener producto por ID"""
        product = self.product_repository.get_by_id_or_404(product_id)
        return product.to_dict()
    
    def get_products(self, page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """Obtener productos con filtros"""
        result = self.product_repository.get_all(page=page, per_page=per_page, **filters)
        return {
            'products': [product.to_dict() for product in result['items']],
            'pagination': result['pagination']
        }
    
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar producto"""
        product = self.product_repository.update(product_id, **product_data)
        return product.to_dict()
    
    def delete_product(self, product_id: int) -> bool:
        """Eliminar producto físicamente"""
        return self.product_repository.delete(product_id)
    
    def get_low_stock_products(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener productos con stock bajo"""
        result = self.product_repository.get_low_stock_products(page=page, per_page=per_page)
        return {
            'products': [product.to_dict() for product in result['items']],
            'pagination': result['pagination']
        }
    
    def get_product_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de productos"""
        return self.product_repository.get_product_stats()
