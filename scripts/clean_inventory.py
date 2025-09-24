from app import create_app
from app.database import db
from app.models import Inventory

app = create_app()

with app.app_context():
    confirm = input("¿Seguro que deseas eliminar TODOS los movimientos de inventario? (s/n): ")
    if confirm.lower() == 's':
        deleted = Inventory.query.delete()
        db.session.commit()
        print(f"{deleted} movimientos de inventario eliminados.")
    else:
        print("Operación cancelada.") 