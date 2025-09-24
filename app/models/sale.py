from sqlalchemy import Column, Integer, Float, String, ForeignKey, Enum, JSON, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.core.database import db

class PaymentMethod(enum.Enum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    OTHER = "other"

class SaleStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Sale(db.Model):
    """Modelo para ventas"""
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(SaleStatus), nullable=False, default=SaleStatus.PENDING)
    sale_metadata = Column(JSON)  # Para datos adicionales como descuentos, impuestos, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    customer = relationship('Customer', back_populates='sales')
    user = relationship('User', back_populates='sales')
    items = relationship('SaleItem', back_populates='sale', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Sale {self.invoice_number}: ${self.total_amount}>'

class SaleItem(db.Model):
    """Modelo para items de venta"""
    __tablename__ = 'sale_items'

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    sale = relationship('Sale', back_populates='items')
    product = relationship('Product', back_populates='sale_items')

    @property
    def total_price(self):
        """Calcula el precio total del item"""
        return (self.quantity * self.unit_price) * (1 - self.discount) 