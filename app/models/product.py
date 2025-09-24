from sqlalchemy import Column, String, Float, Text, JSON, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db

class Product(db.Model):
    """Modelo para productos"""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    category = Column(String(50))
    product_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    inventory = relationship('Inventory', back_populates='product', lazy='dynamic')
    sale_items = relationship('SaleItem', back_populates='product', lazy='dynamic')
    embeddings = relationship('ProductEmbedding', back_populates='product', lazy='dynamic')

    def __repr__(self):
        return f'<Product {self.code}: {self.name}>'
    
    def to_dict(self):
        """Convertir producto a diccionario"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'product_metadata': self.product_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProductEmbedding(db.Model):
    """Modelo para embeddings de productos"""
    __tablename__ = 'product_embeddings'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    embedding_type = Column(String(50), nullable=False)
    embedding = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    product = relationship('Product', back_populates='embeddings') 