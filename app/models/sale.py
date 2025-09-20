"""
Sale Models - Sistema POS O'Data
===============================
Modelos de venta con validaciones enterprise.
"""

from app import db
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Dict, Any, Optional
from decimal import Decimal

class Sale(db.Model):
    """Modelo de venta con validaciones enterprise"""
    
    __tablename__ = 'sales'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    customer_id = db.Column(db.Integer, nullable=True, index=True)  # Referencia a cliente externo
    
    # Totales
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0.0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0.0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, index=True)
    
    # Información de pago
    payment_method = db.Column(db.String(20), default='cash', index=True)
    payment_reference = db.Column(db.String(100), nullable=True)
    change_amount = db.Column(db.Numeric(10, 2), default=0.0)
    
    # Estado
    status = db.Column(db.String(20), default='completed', index=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    items = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')
    # customer = relationship("Customer", back_populates="sales")  # Comentado temporalmente
    
    def __init__(self, user_id: int, items: List[Dict], **kwargs):
        """Constructor con validaciones"""
        self.user_id = user_id
        
        # Calcular totales
        self._calculate_totals(items)
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _calculate_totals(self, items: List[Dict]) -> None:
        """Calcular totales de la venta"""
        self.subtotal = Decimal('0.00')
        
        for item_data in items:
            quantity = int(item_data.get('quantity', 1))
            unit_price = Decimal(str(item_data.get('unit_price', 0)))
            item_total = quantity * unit_price
            self.subtotal += item_total
        
        # Aplicar descuentos y impuestos
        self.tax_amount = Decimal(str(self.tax_amount or 0))
        self.discount_amount = Decimal(str(self.discount_amount or 0))
        
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
    
    def add_item(self, product_id: int, quantity: int, unit_price: float) -> 'SaleItem':
        """Agregar item a la venta"""
        item = SaleItem(
            sale_id=self.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=Decimal(str(unit_price))
        )
        
        db.session.add(item)
        self._recalculate_totals()
        
        return item
    
    def _recalculate_totals(self) -> None:
        """Recalcular totales después de cambios"""
        self.subtotal = sum(item.total_price for item in self.items)
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.updated_at = datetime.utcnow()
    
    def apply_discount(self, discount_amount: float, discount_type: str = 'fixed') -> None:
        """Aplicar descuento a la venta"""
        if discount_type == 'fixed':
            self.discount_amount = Decimal(str(discount_amount))
        elif discount_type == 'percentage':
            self.discount_amount = self.subtotal * Decimal(str(discount_amount)) / 100
        
        self._recalculate_totals()
    
    def apply_tax(self, tax_rate: float) -> None:
        """Aplicar impuesto a la venta"""
        self.tax_amount = self.subtotal * Decimal(str(tax_rate)) / 100
        self._recalculate_totals()
    
    def to_dict(self, include_items: bool = True) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'customer_id': self.customer_id,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'change_amount': float(self.change_amount),
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        
        return data
    
    def __repr__(self) -> str:
        return f'<Sale {self.id}: ${self.total_amount}>'

class SaleItem(db.Model):
    """Modelo de item de venta"""
    
    __tablename__ = 'sale_items'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    
    # Cantidad y precios
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Descuentos específicos del item
    discount_amount = db.Column(db.Numeric(10, 2), default=0.0)
    discount_reason = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, sale_id: int, product_id: int, quantity: int, unit_price: float, **kwargs):
        """Constructor con validaciones"""
        self.sale_id = sale_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = Decimal(str(unit_price))
        self.total_price = self.quantity * self.unit_price
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def apply_discount(self, discount_amount: float, reason: str = None) -> None:
        """Aplicar descuento al item"""
        self.discount_amount = Decimal(str(discount_amount))
        self.discount_reason = reason
        self.total_price = (self.quantity * self.unit_price) - self.discount_amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'sale_id': self.sale_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price),
            'discount_amount': float(self.discount_amount),
            'discount_reason': self.discount_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<SaleItem {self.id}: {self.quantity}x {self.product_id}>'
