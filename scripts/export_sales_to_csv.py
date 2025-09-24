import csv
from app import create_app
from app.database import db
from app.models import Sale, Customer, Product, User

app = create_app()

with app.app_context():
    ventas = Sale.query.all()
    with open('data/exported_sales.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Producto', 'Cantidad', 'Total', 'Usuario', 'Método de pago', 'Cliente'])
        for v in ventas:
            producto = Product.query.get(v.product_id)
            usuario = User.query.get(v.user_id)
            cliente = Customer.query.get(v.customer_id) if v.customer_id else None
            writer.writerow([
                v.id,
                producto.name if producto else '',
                v.quantity,
                v.total,
                usuario.name if usuario else '',
                v.payment_method,
                cliente.name if cliente else ''
            ])
    print("Ventas exportadas a data/exported_sales.csv") 