"""
Repositories Enterprise - Sistema POS O'Data
===========================================
Patrón Repository con interfaces y CRUD operations.
"""

from .base_repository import BaseRepository
from .user_repository import UserRepository
from .product_repository import ProductRepository
from .sale_repository import SaleRepository
from .inventory_repository import InventoryRepository

__all__ = [
    'BaseRepository',
    'UserRepository', 
    'ProductRepository',
    'SaleRepository',
    'InventoryRepository'
]
