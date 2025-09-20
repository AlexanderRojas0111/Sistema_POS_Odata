"""
Product Model - Sistema POS O'Data
=================================
Modelo de producto con validaciones enterprise.
"""

from app import db
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal

class Product(db.Model):
    """Modelo de producto con validaciones enterprise"""
    
    __tablename__ = 'products'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    sku = db.Column(db.String(50), unique=True, nullable=False, index=True)
    barcode = db.Column(db.String(50), unique=True, nullable=True, index=True)
    
    # Precios y costos
    price = db.Column(db.Numeric(10, 2), nullable=False, index=True)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    margin = db.Column(db.Numeric(5, 2), nullable=True)  # Margen en porcentaje
    
    # Inventario
    stock = db.Column(db.Integer, default=0, index=True)
    min_stock = db.Column(db.Integer, default=5)
    max_stock = db.Column(db.Integer, nullable=True)
    reorder_point = db.Column(db.Integer, default=10)
    
    # Categorización
    category = db.Column(db.String(50), index=True)
    brand = db.Column(db.String(50), index=True)
    supplier = db.Column(db.String(100), nullable=True)
    
    # Estado
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_digital = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    sale_items = db.relationship('SaleItem', backref='product', lazy=True)
    inventory_movements = db.relationship('InventoryMovement', backref='product', lazy=True)
    # Nota: Relación store_products se implementará después de la migración a MySQL
    
    def __init__(self, name: str, sku: str, price: float, cost: float = 0.0, **kwargs):
        """Constructor con validaciones"""
        self.name = name
        self.sku = sku
        self.price = Decimal(str(price))
        self.cost = Decimal(str(cost))
        
        # Calcular margen automáticamente
        if self.cost > 0:
            self.margin = ((self.price - self.cost) / self.cost * 100).quantize(Decimal('0.01'))
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def update_price(self, new_price: float) -> None:
        """Actualizar precio y recalcular margen"""
        self.price = Decimal(str(new_price))
        if self.cost > 0:
            self.margin = ((self.price - self.cost) / self.cost * 100).quantize(Decimal('0.01'))
        self.updated_at = datetime.utcnow()
    
    def update_cost(self, new_cost: float) -> None:
        """Actualizar costo y recalcular margen"""
        self.cost = Decimal(str(new_cost))
        if self.cost > 0:
            self.margin = ((self.price - self.cost) / self.cost * 100).quantize(Decimal('0.01'))
        self.updated_at = datetime.utcnow()
    
    def adjust_stock(self, quantity: int, reason: str = "manual_adjustment") -> None:
        """Ajustar stock y crear movimiento de inventario"""
        from app.models.inventory import InventoryMovement
        
        old_stock = self.stock
        self.stock += quantity
        
        # Crear movimiento de inventario
        movement = InventoryMovement(
            product_id=self.id,
            movement_type='adjustment',
            quantity=quantity,
            reason=reason,
            previous_stock=old_stock,
            new_stock=self.stock
        )
        
        db.session.add(movement)
        self.updated_at = datetime.utcnow()
    
    def is_low_stock(self) -> bool:
        """Verificar si el stock está bajo"""
        return self.stock <= self.min_stock
    
    def is_out_of_stock(self) -> bool:
        """Verificar si está agotado"""
        return self.stock <= 0
    
    def needs_reorder(self) -> bool:
        """Verificar si necesita reorden"""
        return self.stock <= self.reorder_point
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'sku': self.sku,
            'barcode': self.barcode,
            'price': float(self.price),
            'cost': float(self.cost) if include_sensitive else None,
            'margin': float(self.margin) if self.margin else None,
            'stock': self.stock,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'reorder_point': self.reorder_point,
            'category': self.category,
            'brand': self.brand,
            'supplier': self.supplier if include_sensitive else None,
            'is_active': self.is_active,
            'is_digital': self.is_digital,
            'is_low_stock': self.is_low_stock(),
            'is_out_of_stock': self.is_out_of_stock(),
            'needs_reorder': self.needs_reorder(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        return data
    
    def __repr__(self) -> str:
        return f'<Product {self.sku}: {self.name}>'
