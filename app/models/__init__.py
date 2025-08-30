"""
Modelos de la aplicación POS
"""

# Importar todos los modelos para que estén disponibles
from .base import Base
from .user import User
from .product import Product
from .inventory import Inventory
from .sale import Sale
from .customer import Customer

__all__ = [
    'Base',
    'User', 
    'Product',
    'Inventory',
    'Sale',
    'Customer'
]
