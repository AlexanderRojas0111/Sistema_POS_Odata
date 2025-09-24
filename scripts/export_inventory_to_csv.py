import csv
from app import create_app
from app.database import db
from app.models import Inventory, Product, User

app = create_app()

with app.app_context():
    movimientos = Inventory.query.all()
    with open('data/exported_inventory.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Producto', 'Cantidad', 'Tipo de movimiento', 'Usuario'])
        for m in movimientos:
            producto = Product.query.get(m.product_id)
            usuario = User.query.get(m.user_id)
            writer.writerow([
                m.id,
                producto.name if producto else '',
                m.quantity,
                m.movement_type,
                usuario.name if usuario else ''
            ])
    print("Movimientos de inventario exportados a data/exported_inventory.csv") 