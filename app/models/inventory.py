"""
Inventory Model - Sistema POS O'Data
===================================
Modelo de inventario con trazabilidad completa.
"""

from app import db
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal

class InventoryMovement(db.Model):
    """Modelo de movimiento de inventario con trazabilidad"""
    
    __tablename__ = 'inventory_movements'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # Información del movimiento
    movement_type = db.Column(db.String(20), nullable=False, index=True)  # sale, purchase, adjustment, transfer
    quantity = db.Column(db.Integer, nullable=False)  # Positivo para entrada, negativo para salida
    reason = db.Column(db.String(100), nullable=True)
    reference_id = db.Column(db.Integer, nullable=True)  # ID de venta, compra, etc.
    reference_type = db.Column(db.String(20), nullable=True)  # sale, purchase, adjustment
    
    # Stock antes y después
    previous_stock = db.Column(db.Integer, nullable=False)
    new_stock = db.Column(db.Integer, nullable=False)
    
    # Información adicional
    notes = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(50), default='main', index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __init__(
        self, 
        product_id: int, 
        movement_type: str, 
        quantity: int, 
        reason: str = None,
        user_id: int = None,
        **kwargs
    ):
        """Constructor con validaciones"""
        self.product_id = product_id
        self.movement_type = movement_type
        self.quantity = quantity
        self.reason = reason
        self.user_id = user_id
        
        # Obtener stock actual del producto
        from app.models.product import Product
        product = Product.query.get(product_id)
        if product:
            self.previous_stock = product.stock
            self.new_stock = product.stock + quantity
        else:
            self.previous_stock = 0
            self.new_stock = quantity
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'movement_type': self.movement_type,
            'quantity': self.quantity,
            'reason': self.reason,
            'reference_id': self.reference_id,
            'reference_type': self.reference_type,
            'previous_stock': self.previous_stock,
            'new_stock': self.new_stock,
            'notes': self.notes,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<InventoryMovement {self.id}: {self.movement_type} {self.quantity}>'
