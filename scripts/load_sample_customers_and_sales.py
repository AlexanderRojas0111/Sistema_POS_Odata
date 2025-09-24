from app import create_app
from app.database import db
from app.models import Customer, Sale, Product, User

app = create_app()

with app.app_context():
    # Crear clientes de ejemplo
    clientes = [
        Customer(name="Juan Pérez", email="juan@example.com", phone="1234567890"),
        Customer(name="Ana Gómez", email="ana@example.com", phone="0987654321"),
    ]
    db.session.add_all(clientes)
    db.session.commit()
    print("Clientes de ejemplo cargados.")

    # Obtener producto y usuario existentes (o crear si no existen)
    producto = Product.query.first()
    if not producto:
        producto = Product(name="Producto Demo", stock=100, price=50.0)
        db.session.add(producto)
        db.session.commit()
    usuario = User.query.first()
    if not usuario:
        usuario = User(email="admin@example.com", password="admin", name="Admin")
        db.session.add(usuario)
        db.session.commit()

    # Crear ventas de ejemplo
    ventas = [
        Sale(product_id=producto.id, quantity=2, total=100.0, user_id=usuario.id, payment_method="efectivo", customer_id=clientes[0].id),
        Sale(product_id=producto.id, quantity=1, total=50.0, user_id=usuario.id, payment_method="tarjeta", customer_id=clientes[1].id),
    ]
    db.session.add_all(ventas)
    db.session.commit()
    print("Ventas de ejemplo cargadas.") 