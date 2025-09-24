import csv
from app import create_app
from app.database import db
from app.models import Product

app = create_app()

with app.app_context():
    productos = Product.query.all()
    with open('data/exported_products.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Nombre', 'Stock', 'Precio'])
        for p in productos:
            writer.writerow([p.id, p.name, p.stock, p.price])
    print("Productos exportados a data/exported_products.csv") 