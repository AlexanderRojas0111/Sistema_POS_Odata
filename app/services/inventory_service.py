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
    
    def __init__(self, inventory_repository: InventoryRepository):
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
