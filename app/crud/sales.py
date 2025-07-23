from app.models import Sale
from app import db

def get_all_sales():
    return Sale.query.all()

def create_sale(data):
    sale = Sale(
        product_id=data.get('product_id'),
        quantity=data.get('quantity'),
        total=data.get('total'),
        user_id=data.get('user_id')
    )
    db.session.add(sale)
    db.session.commit()
    return sale 