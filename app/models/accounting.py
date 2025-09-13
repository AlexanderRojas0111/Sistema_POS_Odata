"""
Accounting Model - Sistema POS Sabrositas
========================================
Modelo para contabilidad automática.
"""

from app import db
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal
import uuid

class AccountingEntry(db.Model):
    """Modelo de asiento contable"""
    
    __tablename__ = 'accounting_entries'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    entry_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Información del asiento
    entry_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(500), nullable=False)
    reference = db.Column(db.String(100), nullable=True)
    
    # Totales
    total_debit = db.Column(db.Numeric(15, 2), nullable=False)
    total_credit = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Estado
    status = db.Column(db.String(20), default='draft')  # draft, posted, reversed
    
    # Referencias
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('electronic_invoices.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posted_at = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    entries = db.relationship('AccountingEntryLine', backref='entry', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, user_id: int, **kwargs):
        """Constructor con validaciones"""
        self.user_id = user_id
        
        # Generar número de asiento
        self.entry_number = self._generate_entry_number()
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_entry_number(self) -> str:
        """Generar número de asiento único"""
        # Formato: AS + Año + Mes + Secuencial (ej: AS2025010001)
        now = datetime.utcnow()
        prefix = f"AS{now.year}{now.month:02d}"
        
        # Buscar último número de la serie
        last_entry = AccountingEntry.query.filter(
            AccountingEntry.entry_number.like(f"{prefix}%")
        ).order_by(AccountingEntry.entry_number.desc()).first()
        
        if last_entry:
            last_number = int(last_entry.entry_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'entry_number': self.entry_number,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'description': self.description,
            'reference': self.reference,
            'total_debit': float(self.total_debit),
            'total_credit': float(self.total_credit),
            'status': self.status,
            'sale_id': self.sale_id,
            'invoice_id': self.invoice_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'entries': [entry.to_dict() for entry in self.entries]
        }
    
    def __repr__(self) -> str:
        return f'<AccountingEntry {self.entry_number}>'

class AccountingEntryLine(db.Model):
    """Modelo de línea de asiento contable"""
    
    __tablename__ = 'accounting_entry_lines'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.Integer, db.ForeignKey('accounting_entries.id'), nullable=False)
    
    # Información contable
    account_code = db.Column(db.String(20), nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    
    # Montos
    debit_amount = db.Column(db.Numeric(15, 2), nullable=False, default=0.0)
    credit_amount = db.Column(db.Numeric(15, 2), nullable=False, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, entry_id: int, **kwargs):
        """Constructor con validaciones"""
        self.entry_id = entry_id
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'entry_id': self.entry_id,
            'account_code': self.account_code,
            'account_name': self.account_name,
            'description': self.description,
            'debit_amount': float(self.debit_amount),
            'credit_amount': float(self.credit_amount),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<AccountingEntryLine {self.id}: {self.account_code}>'

class ChartOfAccounts(db.Model):
    """Modelo de plan de cuentas"""
    
    __tablename__ = 'chart_of_accounts'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    account_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    account_name = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)  # asset, liability, equity, income, expense
    parent_code = db.Column(db.String(20), nullable=True)
    
    # Configuración
    is_active = db.Column(db.Boolean, default=True)
    requires_third_party = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, account_code: str, account_name: str, account_type: str, **kwargs):
        """Constructor con validaciones"""
        self.account_code = account_code
        self.account_name = account_name
        self.account_type = account_type
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'account_code': self.account_code,
            'account_name': self.account_name,
            'account_type': self.account_type,
            'parent_code': self.parent_code,
            'is_active': self.is_active,
            'requires_third_party': self.requires_third_party,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f'<ChartOfAccounts {self.account_code}: {self.account_name}>'
