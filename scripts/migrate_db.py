from app import create_app
from app.database import db

app = create_app()

with app.app_context():
    confirm = input("¿Estás seguro de que quieres borrar y recrear todas las tablas? Esto eliminará todos los datos. (s/n): ")
    if confirm.lower() == 's':
        db.drop_all()
        db.create_all()
        print("Migración completada: Tablas borradas y recreadas según los modelos actuales.")
    else:
        print("Operación cancelada. No se realizaron cambios.") 