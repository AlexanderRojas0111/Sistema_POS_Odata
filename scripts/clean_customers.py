from app import create_app
from app.database import db
from app.models import Customer

app = create_app()

with app.app_context():
    confirm = input("¿Seguro que deseas eliminar TODOS los clientes? (s/n): ")
    if confirm.lower() == 's':
        deleted = Customer.query.delete()
        db.session.commit()
        print(f"{deleted} clientes eliminados.")
    else:
        print("Operación cancelada.") 