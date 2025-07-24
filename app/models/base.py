from app import db
from flask import current_app
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from datetime import datetime
from app.core.database import Base

class BaseModel(Base):
    """Modelo base con campos comunes"""
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convierte el modelo a un diccionario"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    @classmethod
    def from_dict(cls, data):
        """Crea una instancia del modelo desde un diccionario"""
        return cls(**{
            key: value
            for key, value in data.items()
            if key in cls.__table__.columns.keys()
        })

class Product(db.Model):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    stock = Column(Integer, default=0)
    price = Column(Float, nullable=False)
    
    # Agregar relación con ProductEmbedding
    embeddings = relationship("ProductEmbedding", back_populates="product", lazy="dynamic")

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
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    name = Column(String(120), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name
        }

class Customer(db.Model):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True)
    phone = Column(String(30))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone
        }

class Sale(db.Model):
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    total = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    payment_method = Column(String(30), nullable=False)  # efectivo, tarjeta, transferencia
    customer_id = Column(Integer, ForeignKey('customers.id'))

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
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    movement_type = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "movement_type": self.movement_type,
            "user_id": self.user_id
        }

class ProductEmbedding(db.Model):
    __tablename__ = "product_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    embedding = Column(JSON)  # Vector de 768 dimensiones (BERT) almacenado como JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Configurar la relación bidireccional
    product = relationship("Product", back_populates="embeddings")

class DocumentEmbedding(db.Model):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    embedding = Column(JSON)  # Vector almacenado como JSON
    document_type = Column(String)  # 'manual', 'policy', 'description', etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    meta_info = Column(String)  # JSON string con metadatos adicionales