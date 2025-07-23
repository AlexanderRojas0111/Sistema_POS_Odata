from app.models import Product
from app import db

def get_all_products():
    return Product.query.all()

def create_product(data):
    product = Product(
        name=data.get('name'),
        stock=data.get('stock', 0),
        price=data.get('price')
    )
    db.session.add(product)
    db.session.commit()
    return product

def update_product(product_id, data):
    product = Product.query.get_or_404(product_id)
    product.name = data.get('name', product.name)
    product.stock = data.get('stock', product.stock)
    product.price = data.get('price', product.price)
    db.session.commit()
    return product

def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return True 