from app import create_app
from app.database import db
from app.models import Product

app = create_app()

with app.app_context():
    confirm = input("¿Seguro que deseas eliminar TODOS los productos? (s/n): ")
    if confirm.lower() == 's':
        deleted = Product.query.delete()
        db.session.commit()
        print(f"{deleted} productos eliminados.")
    else:
        print("Operación cancelada.") 