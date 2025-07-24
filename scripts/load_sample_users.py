from app import create_app
from app.database import db
from app.models import User
from app.utils.security import hash_password

app = create_app()

with app.app_context():
    usuarios = [
        User(email="admin@example.com", password=hash_password("admin123"), name="Administrador"),
        User(email="cajero@example.com", password=hash_password("cajero123"), name="Cajero"),
        User(email="vendedor@example.com", password=hash_password("vendedor123"), name="Vendedor"),
    ]
    db.session.add_all(usuarios)
    db.session.commit()
    print("Usuarios de ejemplo cargados.") 