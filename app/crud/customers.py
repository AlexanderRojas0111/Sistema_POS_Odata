from app.models import Customer
from app import db

def get_all_customers():
    return Customer.query.all()

def create_customer(data):
    customer = Customer(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone')
    )
    db.session.add(customer)
    db.session.commit()
    return customer 