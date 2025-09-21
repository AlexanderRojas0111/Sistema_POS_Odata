"""
Inventory Service - Sistema POS O'Data
=====================================
Servicio de inventario con lógica de negocio enterprise.
"""

from typing import Dict, Any, Optional, List
from app.repositories.inventory_repository import InventoryRepository
from app.exceptions import ValidationError, BusinessLogicError
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
        """Obtener inventario con filtros"""
        return self.inventory_repository.get_all(page=page, per_page=per_page, **filters)
    
    def get_inventory_summary(self, store_id: Optional[int] = None) -> Dict[str, Any]:
        """Obtener resumen del inventario"""
        # Implementación temporal básica
        return {
            'total_products': 0,
            'low_stock_count': 0,
            'out_of_stock_count': 0,
            'store_id': store_id
        }
    
    def get_low_stock_products(self, store_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener productos con stock bajo"""
        # Implementación temporal básica
        return []
    
    def adjust_inventory(self, product_id: int, quantity: int, reason: str, store_id: Optional[int] = None) -> Dict[str, Any]:
        """Ajustar inventario de un producto"""
        # Implementación temporal básica
        return {
            'product_id': product_id,
            'quantity': quantity,
            'reason': reason,
            'store_id': store_id,
            'adjusted_at': '2025-09-21T13:00:00Z'
        }