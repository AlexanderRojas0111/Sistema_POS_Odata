from sqlalchemy import Column, String, Boolean, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Customer(BaseModel):
    """Modelo para clientes"""
    __tablename__ = 'customers'

    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True)
    phone = Column(String(20))
    address = Column(String(200))
    tax_id = Column(String(50), unique=True)  # RUC/NIT/RFC según el país
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON)  # Para datos adicionales como preferencias, historial, etc.
    
    # Relaciones
    sales = relationship('Sale', back_populates='customer', lazy='dynamic')

    def __repr__(self):
        return f'<Customer {self.name}>'

    @property
    def total_purchases(self):
        """Calcula el total de compras del cliente"""
        return sum(sale.total_amount for sale in self.sales)

    def to_dict(self):
        """Convierte el modelo a un diccionario con datos adicionales"""
        data = super().to_dict()
        data['total_purchases'] = self.total_purchases
        return data 