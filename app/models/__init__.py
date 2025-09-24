# Modelos del Sistema POS Odata
from app.models.user import User
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.customer import Customer
from app.models.sale import Sale

# Exportar todos los modelos
__all__ = [
    'User',
    'Product', 
    'Inventory',
    'Customer',
    'Sale'
]
