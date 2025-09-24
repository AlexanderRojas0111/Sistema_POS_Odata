from sqlalchemy import Column, Integer, Float, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.core.database import db

class InventoryActionType(enum.Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    RETURN = "return"

class Inventory(db.Model):
    """Modelo para movimientos de inventario"""
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    action_type = Column(Enum(InventoryActionType), nullable=False)
    reference = Column(String(100))  # Referencia al documento relacionado (factura, orden, etc.)
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    product = relationship('Product', back_populates='inventory')
    user = relationship('User', back_populates='inventory_changes')

    def __repr__(self):
        return f'<Inventory {self.action_type.value}: {self.quantity} of Product {self.product_id}>' 