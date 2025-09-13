"""
Electronic Invoice Model - Sistema POS Sabrositas
================================================
Modelo para facturación electrónica con integración DIAN.
"""

from app import db
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal
import uuid
import json

class ElectronicInvoice(db.Model):
    """Modelo de factura electrónica"""
    
    __tablename__ = 'electronic_invoices'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    invoice_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Información fiscal
    company_nit = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    customer_nit = db.Column(db.String(20), nullable=True)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_email = db.Column(db.String(100), nullable=True)
    
    # Totales
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    discount_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    
    # Estado fiscal
    fiscal_status = db.Column(db.String(20), default='pending')  # pending, sent, accepted, rejected
    dian_response = db.Column(db.Text, nullable=True)
    cufe = db.Column(db.String(100), nullable=True)  # Código Único de Facturación Electrónica
    
    # Referencias
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, sale_id: int, user_id: int, **kwargs):
        """Constructor con validaciones"""
        self.sale_id = sale_id
        self.user_id = user_id
        
        # Generar número de factura
        self.invoice_number = self._generate_invoice_number()
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_invoice_number(self) -> str:
        """Generar número de factura único"""
        # Formato: FV + Año + Mes + Secuencial (ej: FV2025010001)
        now = datetime.utcnow()
        prefix = f"FV{now.year}{now.month:02d}"
        
        # Buscar último número de la serie
        last_invoice = ElectronicInvoice.query.filter(
            ElectronicInvoice.invoice_number.like(f"{prefix}%")
        ).order_by(ElectronicInvoice.invoice_number.desc()).first()
        
        if last_invoice:
            last_number = int(last_invoice.invoice_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'invoice_number': self.invoice_number,
            'company_nit': self.company_nit,
            'company_name': self.company_name,
            'customer_nit': self.customer_nit,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'fiscal_status': self.fiscal_status,
            'cufe': self.cufe,
            'sale_id': self.sale_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None
        }
    
    def __repr__(self) -> str:
        return f'<ElectronicInvoice {self.invoice_number}>'

class InvoiceItem(db.Model):
    """Modelo de item de factura electrónica"""
    
    __tablename__ = 'invoice_items'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('electronic_invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Información del producto
    product_code = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_description = db.Column(db.Text, nullable=True)
    
    # Cantidades y precios
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(12, 2), nullable=False)
    
    # Impuestos
    tax_rate = db.Column(db.Numeric(5, 2), default=19.0)  # IVA 19%
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, invoice_id: int, product_id: int, **kwargs):
        """Constructor con validaciones"""
        self.invoice_id = invoice_id
        self.product_id = product_id
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'product_id': self.product_id,
            'product_code': self.product_code,
            'product_name': self.product_name,
            'product_description': self.product_description,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price),
            'tax_rate': float(self.tax_rate),
            'tax_amount': float(self.tax_amount),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<InvoiceItem {self.id}: {self.product_name}>'
