from app import create_app
from app.database import db
from app.models import Sale

app = create_app()

with app.app_context():
    confirm = input("¿Seguro que deseas eliminar TODAS las ventas? (s/n): ")
    if confirm.lower() == 's':
        deleted = Sale.query.delete()
        db.session.commit()
        print(f"{deleted} ventas eliminadas.")
    else:
        print("Operación cancelada.") 