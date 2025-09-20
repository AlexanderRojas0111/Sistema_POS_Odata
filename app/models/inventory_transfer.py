"""
Modelo de Transferencias de Inventario - Sistema Multi-Sede
==========================================================
Gestión de transferencias de productos entre tiendas Sabrositas.
"""

from datetime import datetime
from app import db
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Decimal, ForeignKey, Enum
from sqlalchemy.orm import relationship
from dataclasses import dataclass
from typing import List, Optional
import enum

class TransferStatus(enum.Enum):
    """Estados de transferencia de inventario"""
    PENDING = "pending"
    APPROVED = "approved"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class TransferType(enum.Enum):
    """Tipos de transferencia"""
    MANUAL = "manual"           # Transferencia manual
    AUTOMATIC = "automatic"     # Transferencia automática por restock
    EMERGENCY = "emergency"     # Transferencia de emergencia
    REBALANCE = "rebalance"     # Rebalanceo de inventario

@dataclass
class InventoryTransfer(db.Model):
    """Modelo de Transferencia de Inventario entre tiendas"""
    
    __tablename__ = 'inventory_transfers'
    
    # Identificación
    id: int = Column(Integer, primary_key=True)
    transfer_number: str = Column(String(20), unique=True, nullable=False, index=True)
    
    # Tiendas origen y destino
    from_store_id: int = Column(Integer, ForeignKey('stores.id'), nullable=False)
    to_store_id: int = Column(Integer, ForeignKey('stores.id'), nullable=False)
    
    # Estados y tipos
    status: TransferStatus = Column(Enum(TransferStatus), default=TransferStatus.PENDING)
    transfer_type: TransferType = Column(Enum(TransferType), default=TransferType.MANUAL)
    priority: str = Column(String(10), default='normal')  # low, normal, high, urgent
    
    # Información adicional
    reason: str = Column(Text)
    notes: str = Column(Text)
    
    # Usuarios responsables
    requested_by: int = Column(Integer, ForeignKey('users.id'), nullable=False)
    approved_by: int = Column(Integer, ForeignKey('users.id'), nullable=True)
    received_by: int = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Costos y totales
    total_items: int = Column(Integer, default=0)
    total_cost: float = Column(Decimal(12,2), default=0.00)
    shipping_cost: float = Column(Decimal(10,2), default=0.00)
    
    # Timestamps críticos
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    approved_at: datetime = Column(DateTime, nullable=True)
    shipped_at: datetime = Column(DateTime, nullable=True)
    delivered_at: datetime = Column(DateTime, nullable=True)
    expected_delivery: datetime = Column(DateTime, nullable=True)
    
    # Relaciones
    from_store = relationship("Store", foreign_keys=[from_store_id])
    to_store = relationship("Store", foreign_keys=[to_store_id])
    requester = relationship("User", foreign_keys=[requested_by])
    approver = relationship("User", foreign_keys=[approved_by])
    receiver = relationship("User", foreign_keys=[received_by])
    transfer_items = relationship("InventoryTransferItem", back_populates="transfer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Transfer {self.transfer_number}: {self.from_store_id}→{self.to_store_id} ({self.status.value})>'
    
    @property
    def is_pending(self) -> bool:
        """Verificar si la transferencia está pendiente"""
        return self.status == TransferStatus.PENDING
    
    @property
    def is_in_progress(self) -> bool:
        """Verificar si la transferencia está en progreso"""
        return self.status in [TransferStatus.APPROVED, TransferStatus.IN_TRANSIT]
    
    @property
    def is_completed(self) -> bool:
        """Verificar si la transferencia está completada"""
        return self.status == TransferStatus.DELIVERED
    
    @property
    def is_cancelled(self) -> bool:
        """Verificar si la transferencia está cancelada"""
        return self.status in [TransferStatus.CANCELLED, TransferStatus.REJECTED]
    
    @property
    def days_since_created(self) -> int:
        """Días desde la creación"""
        return (datetime.utcnow() - self.created_at).days
    
    @property
    def is_overdue(self) -> bool:
        """Verificar si la transferencia está atrasada"""
        if not self.expected_delivery or self.is_completed:
            return False
        return datetime.utcnow() > self.expected_delivery
    
    def generate_transfer_number(self) -> str:
        """Generar número único de transferencia"""
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M")
        return f"TR{timestamp}{self.from_store_id:02d}{self.to_store_id:02d}"
    
    def approve_transfer(self, approved_by_user_id: int) -> bool:
        """Aprobar transferencia"""
        if self.status != TransferStatus.PENDING:
            return False
        
        self.status = TransferStatus.APPROVED
        self.approved_by = approved_by_user_id
        self.approved_at = datetime.utcnow()
        return True
    
    def ship_transfer(self) -> bool:
        """Marcar transferencia como enviada"""
        if self.status != TransferStatus.APPROVED:
            return False
        
        self.status = TransferStatus.IN_TRANSIT
        self.shipped_at = datetime.utcnow()
        
        # Reducir stock en tienda origen
        for item in self.transfer_items:
            store_product = db.session.query(StoreProduct).filter_by(
                store_id=self.from_store_id,
                product_id=item.product_id
            ).first()
            
            if store_product:
                store_product.adjust_stock(-item.quantity, f"Transfer {self.transfer_number}")
        
        return True
    
    def complete_transfer(self, received_by_user_id: int) -> bool:
        """Completar transferencia"""
        if self.status != TransferStatus.IN_TRANSIT:
            return False
        
        self.status = TransferStatus.DELIVERED
        self.received_by = received_by_user_id
        self.delivered_at = datetime.utcnow()
        
        # Aumentar stock en tienda destino
        for item in self.transfer_items:
            store_product = db.session.query(StoreProduct).filter_by(
                store_id=self.to_store_id,
                product_id=item.product_id
            ).first()
            
            if store_product:
                store_product.adjust_stock(item.received_quantity or item.quantity, 
                                         f"Transfer {self.transfer_number}")
        
        return True
    
    def cancel_transfer(self, reason: str = "") -> bool:
        """Cancelar transferencia"""
        if self.status in [TransferStatus.DELIVERED, TransferStatus.IN_TRANSIT]:
            return False
        
        self.status = TransferStatus.CANCELLED
        if reason:
            self.notes = f"{self.notes or ''}\nCancelled: {reason}".strip()
        
        return True
    
    def calculate_totals(self):
        """Calcular totales de la transferencia"""
        self.total_items = sum(item.quantity for item in self.transfer_items)
        self.total_cost = sum(item.total_cost for item in self.transfer_items)
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para API responses"""
        return {
            'id': self.id,
            'transfer_number': self.transfer_number,
            'from_store_id': self.from_store_id,
            'to_store_id': self.to_store_id,
            'from_store_name': self.from_store.name if self.from_store else None,
            'to_store_name': self.to_store.name if self.to_store else None,
            'status': self.status.value,
            'transfer_type': self.transfer_type.value,
            'priority': self.priority,
            'reason': self.reason,
            'notes': self.notes,
            'total_items': self.total_items,
            'total_cost': float(self.total_cost),
            'shipping_cost': float(self.shipping_cost),
            'is_pending': self.is_pending,
            'is_in_progress': self.is_in_progress,
            'is_completed': self.is_completed,
            'is_cancelled': self.is_cancelled,
            'is_overdue': self.is_overdue,
            'days_since_created': self.days_since_created,
            'created_at': self.created_at.isoformat(),
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'expected_delivery': self.expected_delivery.isoformat() if self.expected_delivery else None,
            'items': [item.to_dict() for item in self.transfer_items]
        }

@dataclass
class InventoryTransferItem(db.Model):
    """Items individuales de una transferencia de inventario"""
    
    __tablename__ = 'inventory_transfer_items'
    
    # Identificación
    id: int = Column(Integer, primary_key=True)
    transfer_id: int = Column(Integer, ForeignKey('inventory_transfers.id'), nullable=False)
    product_id: int = Column(Integer, ForeignKey('products.id'), nullable=False)
    
    # Cantidades
    quantity: int = Column(Integer, nullable=False)
    received_quantity: int = Column(Integer, nullable=True)  # Puede diferir de quantity
    
    # Precios y costos
    unit_cost: float = Column(Decimal(10,2), nullable=False)
    total_cost: float = Column(Decimal(12,2), nullable=False)
    
    # Estado del item
    condition: str = Column(String(20), default='good')  # good, damaged, expired
    notes: str = Column(Text)
    
    # Timestamps
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    transfer = relationship("InventoryTransfer", back_populates="transfer_items")
    product = relationship("Product")
    
    def __repr__(self):
        return f'<TransferItem {self.transfer_id}-{self.product_id}: {self.quantity}>'
    
    @property
    def has_discrepancy(self) -> bool:
        """Verificar si hay discrepancia en cantidades"""
        return self.received_quantity is not None and self.received_quantity != self.quantity
    
    @property
    def discrepancy_quantity(self) -> int:
        """Cantidad de discrepancia"""
        if not self.has_discrepancy:
            return 0
        return (self.received_quantity or 0) - self.quantity
    
    def to_dict(self) -> dict:
        """Convertir a diccionario para API responses"""
        return {
            'id': self.id,
            'transfer_id': self.transfer_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'received_quantity': self.received_quantity,
            'unit_cost': float(self.unit_cost),
            'total_cost': float(self.total_cost),
            'condition': self.condition,
            'notes': self.notes,
            'has_discrepancy': self.has_discrepancy,
            'discrepancy_quantity': self.discrepancy_quantity,
            'created_at': self.created_at.isoformat()
        }

# Importar StoreProduct para evitar circular imports
from app.models.store import StoreProduct
