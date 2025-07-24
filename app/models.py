from app import db
from flask import current_app

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        threshold = current_app.config.get('LOW_STOCK_THRESHOLD', 5)
        alert = None
        if self.stock == 0:
            alert = 'agotado'
        elif self.stock <= threshold:
            alert = 'bajo'
        return {
            "id": self.id,
            "name": self.name,
            "stock": self.stock,
            "price": self.price,
            "alert": alert
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(120), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name
        }

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(30))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone
        }

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False)  # efectivo, tarjeta, transferencia
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "total": self.total,
            "user_id": self.user_id,
            "payment_method": self.payment_method,
            "customer_id": self.customer_id
        }

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    movement_type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "movement_type": self.movement_type,
            "user_id": self.user_id
        }