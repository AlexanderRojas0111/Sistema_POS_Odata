from app.models import Inventory, Product
from app import db

def get_all_inventory():
    return Inventory.query.all()

def create_inventory(data):
    inventory = Inventory(
        product_id=data.get('product_id'),
        quantity=data.get('quantity'),
        movement_type=data.get('movement_type'),
        user_id=data.get('user_id')
    )
    # Actualizar stock según el tipo de movimiento
    product = Product.query.get(inventory.product_id)
    if product:
        if inventory.movement_type.lower() == 'compra':
            product.stock += inventory.quantity
        elif inventory.movement_type.lower() == 'devolucion':
            product.stock += inventory.quantity
        elif inventory.movement_type.lower() == 'ajuste-negativo':
            product.stock = max(0, product.stock - inventory.quantity)
    db.session.add(inventory)
    db.session.commit()
    return inventory 