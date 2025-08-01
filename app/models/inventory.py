from sqlalchemy import Column, Integer, Float, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel

class InventoryActionType(enum.Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    ADJUSTMENT = "adjustment"
    RETURN = "return"

class Inventory(BaseModel):
    """Modelo para movimientos de inventario"""
    __tablename__ = 'inventory'

    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    action_type = Column(Enum(InventoryActionType), nullable=False)
    reference = Column(String(100))  # Referencia al documento relacionado (factura, orden, etc.)
    notes = Column(String(500))
    
    # Relaciones
    product = relationship('Product', back_populates='inventory')
    user = relationship('User', back_populates='inventory_changes')

    def __repr__(self):
        return f'<Inventory {self.action_type.value}: {self.quantity} of Product {self.product_id}>' 