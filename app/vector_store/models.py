from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from .config import VectorBase

class ProductEmbedding(VectorBase):
    __tablename__ = "product_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    embedding = Column(ARRAY(Float))  # Vector de 768 dimensiones (BERT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="embeddings")

class DocumentEmbedding(VectorBase):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    embedding = Column(ARRAY(Float))
    document_type = Column(String)  # 'manual', 'policy', 'description', etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(String)  # JSON string con metadatos adicionales 