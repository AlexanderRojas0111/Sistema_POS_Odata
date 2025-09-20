"""
Accounts Receivable Models - Sistema POS Sabrositas
==================================================
Modelos para gestión de cartera y cuentas por cobrar.
"""

from app import db
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from decimal import Decimal
import uuid

class Customer(db.Model):
    """Modelo de cliente para cartera"""
    
    __tablename__ = 'customers'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    customer_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Información personal/empresarial
    name = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(10), nullable=False)  # CC, CE, NIT, etc.
    document_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(300), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    
    # Información comercial
    customer_type = db.Column(db.String(20), default='individual')  # individual, business
    credit_limit = db.Column(db.Numeric(15, 2), default=0.0)
    payment_terms = db.Column(db.Integer, default=30)  # días
    discount_percentage = db.Column(db.Numeric(5, 2), default=0.0)
    
    # Estado
    is_active = db.Column(db.Boolean, default=True, index=True)
    status = db.Column(db.String(20), default='active')  # active, inactive, blocked
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    invoices = db.relationship('Invoice', backref='customer', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        """Constructor con validaciones"""
        # Generar código de cliente
        self.customer_code = self._generate_customer_code()
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_customer_code(self) -> str:
        """Generar código de cliente único"""
        # Formato: CLI + Año + Secuencial (ej: CLI2025001)
        now = datetime.utcnow()
        prefix = f"CLI{now.year}"
        
        # Buscar último número de la serie
        last_customer = Customer.query.filter(
            Customer.customer_code.like(f"{prefix}%")
        ).order_by(Customer.customer_code.desc()).first()
        
        if last_customer:
            last_number = int(last_customer.customer_code[-3:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:03d}"
    
    @property
    def current_balance(self) -> Decimal:
        """Saldo actual del cliente"""
        total_invoices = sum(float(inv.total_amount) for inv in self.invoices if inv.status != 'cancelled')
        total_payments = sum(float(pay.amount) for pay in self.payments if pay.status == 'completed')
        return Decimal(str(total_invoices - total_payments))
    
    @property
    def is_overdue(self) -> bool:
        """Verificar si tiene facturas vencidas"""
        today = date.today()
        overdue_invoices = Invoice.query.filter(
            Invoice.customer_id == self.id,
            Invoice.due_date < today,
            Invoice.status.in_(['pending', 'partial'])
        ).count()
        return overdue_invoices > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'customer_code': self.customer_code,
            'name': self.name,
            'document_type': self.document_type,
            'document_number': self.document_number,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'department': self.department,
            'customer_type': self.customer_type,
            'credit_limit': float(self.credit_limit),
            'payment_terms': self.payment_terms,
            'discount_percentage': float(self.discount_percentage),
            'is_active': self.is_active,
            'status': self.status,
            'current_balance': float(self.current_balance),
            'is_overdue': self.is_overdue,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f'<Customer {self.customer_code}: {self.name}>'

class Invoice(db.Model):
    """Modelo de factura para cartera"""
    
    __tablename__ = 'accounts_receivable_invoices'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    invoice_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Referencias
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Información de la factura
    invoice_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    payment_terms = db.Column(db.Integer, nullable=False, default=30)
    
    # Montos
    subtotal = db.Column(db.Numeric(15, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(15, 2), default=0.0)
    discount_amount = db.Column(db.Numeric(15, 2), default=0.0)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(15, 2), default=0.0)
    balance_amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Estado
    status = db.Column(db.String(20), default='pending')  # pending, partial, paid, overdue, cancelled
    
    # Información adicional
    notes = db.Column(db.Text, nullable=True)
    reference = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    items = db.relationship('AccountsReceivableInvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='invoice', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, customer_id: int, user_id: int, **kwargs):
        """Constructor con validaciones"""
        self.customer_id = customer_id
        self.user_id = user_id
        self.invoice_number = self._generate_invoice_number()
        
        # Calcular fecha de vencimiento
        if 'due_date' not in kwargs:
            self.due_date = date.today() + timedelta(days=self.payment_terms)
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_invoice_number(self) -> str:
        """Generar número de factura único"""
        # Formato: FAC + Año + Mes + Secuencial (ej: FAC2025010001)
        now = datetime.utcnow()
        prefix = f"FAC{now.year}{now.month:02d}"
        
        # Buscar último número de la serie
        last_invoice = Invoice.query.filter(
            Invoice.invoice_number.like(f"{prefix}%")
        ).order_by(Invoice.invoice_number.desc()).first()
        
        if last_invoice:
            last_number = int(last_invoice.invoice_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    @property
    def is_overdue(self) -> bool:
        """Verificar si la factura está vencida"""
        return self.due_date < date.today() and self.status in ['pending', 'partial']
    
    @property
    def days_overdue(self) -> int:
        """Días de vencimiento"""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days
    
    def calculate_balance(self) -> None:
        """Calcular saldo pendiente"""
        total_paid = sum(float(pay.amount) for pay in self.payments if pay.status == 'completed')
        self.paid_amount = Decimal(str(total_paid))
        self.balance_amount = self.total_amount - self.paid_amount
        
        # Actualizar estado
        if self.balance_amount <= 0:
            self.status = 'paid'
            self.paid_at = datetime.utcnow()
        elif self.paid_amount > 0:
            self.status = 'partial'
        elif self.is_overdue:
            self.status = 'overdue'
        else:
            self.status = 'pending'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'invoice_number': self.invoice_number,
            'customer_id': self.customer_id,
            'sale_id': self.sale_id,
            'user_id': self.user_id,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'payment_terms': self.payment_terms,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'paid_amount': float(self.paid_amount),
            'balance_amount': float(self.balance_amount),
            'status': self.status,
            'notes': self.notes,
            'reference': self.reference,
            'is_overdue': self.is_overdue,
            'days_overdue': self.days_overdue,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None
        }
    
    def __repr__(self) -> str:
        return f'<Invoice {self.invoice_number}>'

class AccountsReceivableInvoiceItem(db.Model):
    """Modelo de item de factura de cuentas por cobrar"""
    
    __tablename__ = 'accounts_receivable_invoice_items'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('accounts_receivable_invoices.id'), nullable=False)
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
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, invoice_id: int, **kwargs):
        """Constructor con validaciones"""
        self.invoice_id = invoice_id
        
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
            'product_name': self.product_name,
            'product_code': self.product_code,
            'description': self.description,
            'quantity': float(self.quantity),
            'unit_price': float(self.unit_price),
            'discount_percentage': float(self.discount_percentage),
            'discount_amount': float(self.discount_amount),
            'total_amount': float(self.total_amount),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<AccountsReceivableInvoiceItem {self.id}: {self.product_name}>'

class Payment(db.Model):
    """Modelo de pago"""
    
    __tablename__ = 'payments'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    payment_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Referencias
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('accounts_receivable_invoices.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Información del pago
    payment_date = db.Column(db.Date, nullable=False, default=date.today)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, card, nequi, daviplata, tullave, check
    reference = db.Column(db.String(100), nullable=True)
    
    # Estado
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    
    # Información adicional
    notes = db.Column(db.Text, nullable=True)
    bank_name = db.Column(db.String(100), nullable=True)
    check_number = db.Column(db.String(50), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, customer_id: int, user_id: int, **kwargs):
        """Constructor con validaciones"""
        self.customer_id = customer_id
        self.user_id = user_id
        self.payment_number = self._generate_payment_number()
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_payment_number(self) -> str:
        """Generar número de pago único"""
        # Formato: PAG + Año + Mes + Secuencial (ej: PAG2025010001)
        now = datetime.utcnow()
        prefix = f"PAG{now.year}{now.month:02d}"
        
        # Buscar último número de la serie
        last_payment = Payment.query.filter(
            Payment.payment_number.like(f"{prefix}%")
        ).order_by(Payment.payment_number.desc()).first()
        
        if last_payment:
            last_number = int(last_payment.payment_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'payment_number': self.payment_number,
            'customer_id': self.customer_id,
            'invoice_id': self.invoice_id,
            'user_id': self.user_id,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'amount': float(self.amount),
            'payment_method': self.payment_method,
            'reference': self.reference,
            'status': self.status,
            'notes': self.notes,
            'bank_name': self.bank_name,
            'check_number': self.check_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self) -> str:
        return f'<Payment {self.payment_number}>'

class PaymentAllocation(db.Model):
    """Modelo de asignación de pagos a facturas"""
    
    __tablename__ = 'payment_allocations'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey('accounts_receivable_invoices.id'), nullable=False)
    
    # Montos
    allocated_amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, payment_id: int, invoice_id: int, allocated_amount: Decimal):
        """Constructor con validaciones"""
        self.payment_id = payment_id
        self.invoice_id = invoice_id
        self.allocated_amount = allocated_amount
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'invoice_id': self.invoice_id,
            'allocated_amount': float(self.allocated_amount),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        return f'<PaymentAllocation {self.id}: {self.allocated_amount}>'
