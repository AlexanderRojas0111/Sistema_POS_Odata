"""
Modelo de Tienda - Sistema Multi-Sede Sabrositas
===============================================
Gestión centralizada de tiendas con soporte para escalabilidad enterprise.
"""

from datetime import datetime
from app import db
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Store(db.Model):
    """Modelo de Tienda para arquitectura multi-sede"""
    
    __tablename__ = 'stores'
    
    # Campos principales
    id: int = Column(Integer, primary_key=True)
    code: str = Column(String(10), unique=True, nullable=False, index=True)
    name: str = Column(String(100), nullable=False)
    address: str = Column(Text)
    phone: str = Column(String(20))
    email: str = Column(String(100))
    
    # Gestión operativa
    manager_id: int = Column(Integer, ForeignKey('users.id'), nullable=True)
    region: str = Column(String(50))
    store_type: str = Column(String(20), default='retail')  # retail, warehouse, franchise
    
    # Estados y configuración
    is_active: bool = Column(Boolean, default=True)
    is_main_store: bool = Column(Boolean, default=False)
    timezone: str = Column(String(50), default='America/Bogota')
    
    # Configuración operativa
    max_concurrent_sales: int = Column(Integer, default=10)
    auto_sync_inventory: bool = Column(Boolean, default=True)
    sync_frequency_minutes: int = Column(Integer, default=15)
    
    # Configuración financiera
    tax_rate: float = Column(Numeric(5,4), default=0.1900)  # 19% IVA Colombia
    currency: str = Column(String(3), default='COP')
    
    # Timestamps
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync_at: datetime = Column(DateTime, nullable=True)
    
    # Relaciones (comentadas temporalmente hasta implementar FK correctas)
    # manager = relationship("User", foreign_keys=[manager_id])
    # store_products = relationship("StoreProduct", back_populates="store", cascade="all, delete-orphan")
    # inventory_movements = relationship("InventoryMovement", foreign_keys="InventoryMovement.store_id")
    # sales = relationship("Sale", back_populates="store")
    # transfers_sent = relationship("InventoryTransfer", foreign_keys="InventoryTransfer.from_store_id")
    # transfers_received = relationship("InventoryTransfer", foreign_keys="InventoryTransfer.to_store_id")
    
    def __repr__(self):
        return f'<Store {self.code}: {self.name}>'
    
    @property
    def is_online(self) -> bool:
        """Verificar si la tienda está en línea (última sincronización < 30 min)"""
        if not self.last_sync_at:
            return False
        
        from datetime import timedelta
        return (datetime.utcnow() - self.last_sync_at) < timedelta(minutes=30)
    
    # Métodos comentados temporalmente hasta implementar relaciones
    # @property
    # def total_products(self) -> int:
    #     """Número total de productos en esta tienda"""
    #     return len([sp for sp in self.store_products if sp.is_available])
    
    # @property
    # def low_stock_products(self) -> int:
    #     """Productos con stock bajo en esta tienda"""
    #     return len([sp for sp in self.store_products 
    #                if sp.current_stock <= sp.min_stock and sp.is_available])
    
    # def get_product_price(self, product_id: int) -> Optional[float]:
    #     """Obtener precio específico de un producto en esta tienda"""
    #     store_product = next(
    #         (sp for sp in self.store_products if sp.product_id == product_id), 
    #         None
    #     )
    #     return store_product.local_price if store_product else None
    
    # def get_product_stock(self, product_id: int) -> int:
    #     """Obtener stock actual de un producto en esta tienda"""
    #     store_product = next(
    #         (sp for sp in self.store_products if sp.product_id == product_id), 
    #         None
    #     )
    #     return store_product.current_stock if store_product else 0
    
    def update_sync_timestamp(self):
        """Actualizar timestamp de última sincronización"""
        self.last_sync_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para API responses"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'region': self.region,
            'store_type': self.store_type,
            'is_active': self.is_active,
            'is_main_store': self.is_main_store,
            'is_online': self.is_online,
            'timezone': self.timezone,
            'tax_rate': float(self.tax_rate),
            'currency': self.currency,
            'total_products': self.total_products,
            'low_stock_products': self.low_stock_products,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None
        }

@dataclass  
class StoreProduct(db.Model):
    """Relación Tienda-Producto con precios y stock locales"""
    
    __tablename__ = 'store_products'
    
    # Clave compuesta
    store_id: int = Column(Integer, ForeignKey('stores.id'), primary_key=True)
    product_id: int = Column(Integer, ForeignKey('products.id'), primary_key=True)
    
    # Precios locales
    local_price: float = Column(Numeric(10,2), nullable=False)
    cost_price: float = Column(Numeric(10,2), nullable=True)
    
    # Gestión de inventario
    current_stock: int = Column(Integer, default=0)
    min_stock: int = Column(Integer, default=5)
    max_stock: int = Column(Integer, default=100)
    reorder_point: int = Column(Integer, default=10)
    
    # Estados
    is_available: bool = Column(Boolean, default=True)
    is_featured: bool = Column(Boolean, default=False)
    
    # Configuración
    allow_negative_stock: bool = Column(Boolean, default=False)
    track_expiration: bool = Column(Boolean, default=True)
    
    # Timestamps
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sale_at: datetime = Column(DateTime, nullable=True)
    
    # Relaciones (comentadas temporalmente)
    # store = relationship("Store", back_populates="store_products")
    # product = relationship("Product", back_populates="store_products")
    
    def __repr__(self):
        return f'<StoreProduct Store:{self.store_id} Product:{self.product_id} Stock:{self.current_stock}>'
    
    @property
    def is_low_stock(self) -> bool:
        """Verificar si el producto tiene stock bajo"""
        return self.current_stock <= self.min_stock
    
    @property
    def is_out_of_stock(self) -> bool:
        """Verificar si el producto está agotado"""
        return self.current_stock <= 0
    
    @property
    def profit_margin(self) -> float:
        """Calcular margen de ganancia"""
        if not self.cost_price or self.cost_price == 0:
            return 0.0
        return ((self.local_price - self.cost_price) / self.cost_price) * 100
    
    def adjust_stock(self, quantity: int, reason: str = "adjustment") -> bool:
        """Ajustar stock con validaciones"""
        new_stock = self.current_stock + quantity
        
        if new_stock < 0 and not self.allow_negative_stock:
            return False
        
        self.current_stock = new_stock
        self.updated_at = datetime.utcnow()
        
        # Registrar movimiento de inventario
        from app.models.inventory_movement import InventoryMovement
        movement = InventoryMovement(
            store_id=self.store_id,
            product_id=self.product_id,
            movement_type='adjustment',
            quantity=quantity,
            reason=reason,
            previous_stock=self.current_stock - quantity,
            new_stock=self.current_stock
        )
        db.session.add(movement)
        
        return True
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para API responses"""
        return {
            'store_id': self.store_id,
            'product_id': self.product_id,
            'local_price': float(self.local_price),
            'cost_price': float(self.cost_price) if self.cost_price else None,
            'current_stock': self.current_stock,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'reorder_point': self.reorder_point,
            'is_available': self.is_available,
            'is_featured': self.is_featured,
            'is_low_stock': self.is_low_stock,
            'is_out_of_stock': self.is_out_of_stock,
            'profit_margin': self.profit_margin,
            'allow_negative_stock': self.allow_negative_stock,
            'track_expiration': self.track_expiration,
            'last_sale_at': self.last_sale_at.isoformat() if self.last_sale_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
