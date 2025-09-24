import pandas as pd
from app import create_app
from app.database import db
from app.models import Product

app = create_app()

with app.app_context():
    df = pd.read_csv('data/products.csv')
    for _, row in df.iterrows():
        product = Product(name=row['name'], stock=row['stock'], price=row['price'])
        db.session.add(product)
    db.session.commit()
    print("Datos de ejemplo cargados en la tabla Product.") 