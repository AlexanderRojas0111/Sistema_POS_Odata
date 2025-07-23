from app.models import Inventory
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
    db.session.add(inventory)
    db.session.commit()
    return inventory 