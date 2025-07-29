from sqlalchemy import Column, String, Float, Text, JSON, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Product(BaseModel):
    """Modelo para productos"""
    __tablename__ = 'products'

    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String(50))
    product_metadata = Column(JSON)
    
    # Relaciones
    inventory = relationship('Inventory', back_populates='product', lazy='dynamic')
    sales = relationship('Sale', back_populates='product', lazy='dynamic')
    embeddings = relationship('ProductEmbedding', back_populates='product', lazy='dynamic')

    def __repr__(self):
        return f'<Product {self.code}: {self.name}>'

class ProductEmbedding(BaseModel):
    """Modelo para embeddings de productos"""
    __tablename__ = 'product_embeddings'

    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    embedding_type = Column(String(50), nullable=False)
    embedding = Column(JSON, nullable=False)
    
    # Relaciones
    product = relationship('Product', back_populates='embeddings') 