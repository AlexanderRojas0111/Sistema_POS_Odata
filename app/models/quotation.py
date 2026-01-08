"""
Quotation Models - Sistema POS Sabrositas
========================================
Modelos para gestión de cotizaciones y presupuestos.
"""

from app import db
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal
import uuid

class Quotation(db.Model):
    """Modelo de cotización"""
    
    __tablename__ = 'quotations'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    quotation_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Referencias
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Información de la cotización
    quotation_date = db.Column(db.Date, nullable=False, default=date.today)
    valid_until = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Montos
    subtotal = db.Column(db.Numeric(15, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(15, 2), default=0.0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0.0)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Estado y flujo de aprobación
    status = db.Column(db.String(20), default='draft')  # draft, pending, approved, rejected, expired, converted
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Información de aprobación
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Información de conversión
    converted_to_sale = db.Column(db.Boolean, default=False)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=True)
    converted_at = db.Column(db.DateTime, nullable=True)
    
    # Información adicional
    notes = db.Column(db.Text, nullable=True)
    terms_conditions = db.Column(db.Text, nullable=True)
    delivery_time = db.Column(db.String(100), nullable=True)
    payment_terms = db.Column(db.String(200), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    items = db.relationship('QuotationItem', backref='quotation', lazy=True, cascade='all, delete-orphan')
    approvals = db.relationship('QuotationApproval', backref='quotation', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, customer_id: int, user_id: int, **kwargs):
        """Constructor con validaciones"""
        self.customer_id = customer_id
        self.user_id = user_id
        self.quotation_number = self._generate_quotation_number()
        
        # Calcular fecha de vencimiento (30 días por defecto)
        if 'valid_until' not in kwargs:
            self.valid_until = date.today() + timedelta(days=30)
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_quotation_number(self) -> str:
        """Generar número de cotización único"""
        # Formato: COT + Año + Mes + Secuencial (ej: COT2025010001)
        now = datetime.utcnow()
        prefix = f"COT{now.year}{now.month:02d}"
        
        # Buscar último número de la serie
        last_quotation = Quotation.query.filter(
            Quotation.quotation_number.like(f"{prefix}%")
        ).order_by(Quotation.quotation_number.desc()).first()
        
        if last_quotation:
            last_number = int(last_quotation.quotation_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    @property
    def is_expired(self) -> bool:
        """Verificar si la cotización está vencida"""
        return self.valid_until < date.today() and self.status in ['draft', 'pending']
    
    @property
    def days_until_expiry(self) -> int:
        """Días hasta el vencimiento"""
        if self.is_expired:
            return 0
        return (self.valid_until - date.today()).days
    
    @property
    def can_be_approved(self) -> bool:
        """Verificar si puede ser aprobada"""
        return self.status in ['draft', 'pending'] and not self.is_expired
    
    @property
    def can_be_converted(self) -> bool:
        """Verificar si puede ser convertida a venta"""
        return self.status == 'approved' and not self.converted_to_sale
    
    def calculate_totals(self) -> None:
        """Calcular totales de la cotización"""
        self.subtotal = sum(float(item.total_amount) for item in self.items)
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'quotation_number': self.quotation_number,
            'customer_id': self.customer_id,
            'user_id': self.user_id,
            'quotation_date': self.quotation_date.isoformat() if self.quotation_date else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'title': self.title,
            'description': self.description,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'status': self.status,
            'priority': self.priority,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejection_reason': self.rejection_reason,
            'converted_to_sale': self.converted_to_sale,
            'sale_id': self.sale_id,
            'converted_at': self.converted_at.isoformat() if self.converted_at else None,
            'notes': self.notes,
            'terms_conditions': self.terms_conditions,
            'delivery_time': self.delivery_time,
            'payment_terms': self.payment_terms,
            'is_expired': self.is_expired,
            'days_until_expiry': self.days_until_expiry,
            'can_be_approved': self.can_be_approved,
            'can_be_converted': self.can_be_converted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f'<Quotation {self.quotation_number}>'

class QuotationItem(db.Model):
    """Modelo de item de cotización"""
    
    __tablename__ = 'quotation_items'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotations.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    
    # Información del producto
    product_name = db.Column(db.String(200), nullable=False)
    product_code = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Cantidades y precios
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price = db.Column(db.Numeric(15, 2), nullable=False)
    discount_percentage = db.Column(db.Numeric(5, 2), default=0.0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0.0)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Información adicional
    notes = db.Column(db.Text, nullable=True)
    delivery_time = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, quotation_id: int, **kwargs):
        """Constructor con validaciones"""
        self.quotation_id = quotation_id
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def calculate_totals(self) -> None:
        """Calcular totales del item"""
        self.discount_amount = (self.quantity * self.unit_price * self.discount_percentage) / 100
        self.total_amount = (self.quantity * self.unit_price) - self.discount_amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'quotation_id': self.quotation_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_code': self.product_code,
            'description': self.description,
            'quantity': float(self.quantity),
            'unit_price': float(self.unit_price),
            'discount_percentage': float(self.discount_percentage),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'notes': self.notes,
            'delivery_time': self.delivery_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<QuotationItem {self.id}: {self.product_name}>'

class QuotationApproval(db.Model):
    """Modelo de aprobación de cotización"""
    
    __tablename__ = 'quotation_approvals'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    quotation_id = db.Column(db.Integer, db.ForeignKey('quotations.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Información de la aprobación
    action = db.Column(db.String(20), nullable=False)  # approve, reject, request_changes
    comments = db.Column(db.Text, nullable=True)
    approval_level = db.Column(db.Integer, default=1)  # Nivel de aprobación
    
    # Estado
    status = db.Column(db.String(20), default='pending')  # pending, completed
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, quotation_id: int, approver_id: int, action: str, **kwargs):
        """Constructor con validaciones"""
        self.quotation_id = quotation_id
        self.approver_id = approver_id
        self.action = action
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'quotation_id': self.quotation_id,
            'approver_id': self.approver_id,
            'action': self.action,
            'comments': self.comments,
            'approval_level': self.approval_level,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self) -> str:
        return f'<QuotationApproval {self.id}: {self.action}>'

class QuotationTemplate(db.Model):
    """Modelo de plantilla de cotización"""
    
    __tablename__ = 'quotation_templates'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    template_name = db.Column(db.String(100), nullable=False)
    
    # Contenido de la plantilla
    title_template = db.Column(db.String(200), nullable=True)
    description_template = db.Column(db.Text, nullable=True)
    terms_conditions_template = db.Column(db.Text, nullable=True)
    delivery_time_default = db.Column(db.String(100), nullable=True)
    payment_terms_default = db.Column(db.String(200), nullable=True)
    
    # Configuración
    default_validity_days = db.Column(db.Integer, default=30)
    requires_approval = db.Column(db.Boolean, default=True)
    approval_levels = db.Column(db.Integer, default=1)
    
    # Estado
    is_active = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, template_name: str, **kwargs):
        """Constructor con validaciones"""
        self.template_name = template_name
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'template_name': self.template_name,
            'title_template': self.title_template,
            'description_template': self.description_template,
            'terms_conditions_template': self.terms_conditions_template,
            'delivery_time_default': self.delivery_time_default,
            'payment_terms_default': self.payment_terms_default,
            'default_validity_days': self.default_validity_days,
            'requires_approval': self.requires_approval,
            'approval_levels': self.approval_levels,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f'<QuotationTemplate {self.template_name}>'
