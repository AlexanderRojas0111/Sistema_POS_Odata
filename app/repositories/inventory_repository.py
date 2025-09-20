"""
Inventory Repository - Sistema POS O'Data
========================================
Repository específico para inventario con operaciones especializadas.
"""

from typing import Optional, List, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.inventory import InventoryMovement
from app.exceptions import ValidationError, NotFoundError
from app import db

class InventoryRepository(BaseRepository[InventoryMovement]):
    """Repository para movimientos de inventario con operaciones especializadas"""
    
    def __init__(self):
        super().__init__(InventoryMovement)
    
    def get_movements_by_product(self, product_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener movimientos por producto"""
        return self.get_all(page=page, per_page=per_page, product_id=product_id)
    
    def get_movements_by_type(self, movement_type: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener movimientos por tipo"""
        return self.get_all(page=page, per_page=per_page, movement_type=movement_type)
    
    def get_inventory_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de inventario"""
        from sqlalchemy import func
        from datetime import datetime, date, timedelta
        
        # Estadísticas generales
        total_movements = self.count()
        
        # Movimientos del día
        today = date.today()
        today_movements = InventoryMovement.query.filter(
            func.date(InventoryMovement.created_at) == today
        ).count()
        
        # Movimientos por tipo
        movement_types = db.session.query(
            InventoryMovement.movement_type,
            func.count(InventoryMovement.id).label('count')
        ).group_by(InventoryMovement.movement_type).all()
        
        movement_stats = {mov_type: count for mov_type, count in movement_types}
        
        return {
            'total_movements': total_movements,
            'today_movements': today_movements,
            'movement_types': movement_stats
        }
