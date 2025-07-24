from app.models import Sale, Product
from app import db

def get_all_sales():
    return Sale.query.all()

def create_sale(data):
    sale = Sale(
        product_id=data.get('product_id'),
        quantity=data.get('quantity'),
        total=data.get('total'),
        user_id=data.get('user_id'),
        payment_method=data.get('payment_method'),
        customer_id=data.get('customer_id')
    )
    # Actualizar stock del producto
    product = Product.query.get(sale.product_id)
    if product:
        if product.stock < sale.quantity:
            raise ValueError('Stock insuficiente para la venta')
        product.stock -= sale.quantity
    db.session.add(sale)
    db.session.commit()
    return sale 