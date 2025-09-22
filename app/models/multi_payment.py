"""
Multi Payment Models - Sistema POS O'Data
=========================================
Modelos para manejar pagos múltiples en ventas.
"""

from app import db
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
import uuid

class MultiPayment(db.Model):
    """Modelo para pagos múltiples en una venta"""
    
    __tablename__ = 'multi_payments'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Referencias
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Información del pago múltiple
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    total_paid = db.Column(db.Numeric(15, 2), default=0.0)
    remaining_amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Estado
    status = db.Column(db.String(20), default='pending')  # pending, partial, completed, cancelled
    
    # Información adicional
    notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    payment_details = db.relationship('PaymentDetail', backref='multi_payment', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, sale_id: int, user_id: int, total_amount: Decimal, **kwargs):
        """Constructor con validaciones"""
        self.sale_id = sale_id
        self.user_id = user_id
        self.total_amount = total_amount
        self.remaining_amount = total_amount
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def add_payment_detail(self, payment_method: str, amount: Decimal, reference: str = None, **kwargs):
        """Agregar detalle de pago"""
        if amount <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        if self.total_paid + amount > self.total_amount:
            raise ValueError("El monto excede el total de la venta")
        
        payment_detail = PaymentDetail(
            multi_payment_id=self.id,
            payment_method=payment_method,
            amount=amount,
            reference=reference,
            **kwargs
        )
        
        db.session.add(payment_detail)
        
        # Actualizar totales
        self.total_paid += amount
        self.remaining_amount = self.total_amount - self.total_paid
        
        # Actualizar estado
        if self.remaining_amount <= 0:
            self.status = 'completed'
            self.completed_at = datetime.utcnow()
        elif self.total_paid > 0:
            self.status = 'partial'
        
        return payment_detail
    
    def remove_payment_detail(self, payment_detail_id: int):
        """Remover detalle de pago"""
        payment_detail = PaymentDetail.query.get(payment_detail_id)
        if payment_detail and payment_detail.multi_payment_id == self.id:
            # Restar del total pagado
            self.total_paid -= payment_detail.amount
            self.remaining_amount = self.total_amount - self.total_paid
            
            # Actualizar estado
            if self.total_paid == 0:
                self.status = 'pending'
            elif self.total_paid > 0:
                self.status = 'partial'
            
            # Eliminar el detalle
            db.session.delete(payment_detail)
            return True
        return False
    
    def get_payment_summary(self) -> Dict[str, Any]:
        """Obtener resumen de pagos"""
        summary = {
            'total_amount': float(self.total_amount),
            'total_paid': float(self.total_paid),
            'remaining_amount': float(self.remaining_amount),
            'status': self.status,
            'payment_methods': {}
        }
        
        # Agrupar por método de pago
        for detail in self.payment_details:
            method = detail.payment_method
            if method not in summary['payment_methods']:
                summary['payment_methods'][method] = {
                    'total': 0.0,
                    'count': 0,
                    'details': []
                }
            
            summary['payment_methods'][method]['total'] += float(detail.amount)
            summary['payment_methods'][method]['count'] += 1
            summary['payment_methods'][method]['details'].append({
                'id': detail.id,
                'amount': float(detail.amount),
                'reference': detail.reference,
                'created_at': detail.created_at.isoformat()
            })
        
        return summary
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'sale_id': self.sale_id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount),
            'total_paid': float(self.total_paid),
            'remaining_amount': float(self.remaining_amount),
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'payment_summary': self.get_payment_summary()
        }
    
    def __repr__(self):
        return f'<MultiPayment {self.id}: ${self.total_paid}/{self.total_amount} ({self.status})>'

class PaymentDetail(db.Model):
    """Modelo para detalles individuales de pago"""
    
    __tablename__ = 'payment_details'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Referencias
    multi_payment_id = db.Column(db.Integer, db.ForeignKey('multi_payments.id'), nullable=False)
    
    # Información del pago
    payment_method = db.Column(db.String(30), nullable=False)  # cash, card, nequi, daviplata, etc.
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    reference = db.Column(db.String(100), nullable=True)  # Número de transacción, referencia, etc.
    
    # Información adicional específica del método
    bank_name = db.Column(db.String(100), nullable=True)  # Para tarjetas
    card_last_four = db.Column(db.String(4), nullable=True)  # Últimos 4 dígitos de tarjeta
    phone_number = db.Column(db.String(20), nullable=True)  # Para Nequi, Daviplata
    qr_code = db.Column(db.String(200), nullable=True)  # Para pagos QR
    
    # Estado
    status = db.Column(db.String(20), default='completed')  # pending, completed, failed, refunded
    
    # Información adicional
    notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, multi_payment_id: int, payment_method: str, amount: Decimal, **kwargs):
        """Constructor con validaciones"""
        self.multi_payment_id = multi_payment_id
        self.payment_method = payment_method
        self.amount = amount
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_payment_method_display(self) -> str:
        """Obtener nombre legible del método de pago"""
        method_names = {
            'cash': '💵 Efectivo',
            'card': '💳 Tarjeta',
            'nequi': '📱 Nequi',
            'nequi_qr': '📱 Nequi QR',
            'daviplata': '🟣 Daviplata',
            'daviplata_qr': '🟣 Daviplata QR',
            'qr_generic': '📲 QR Genérico',
            'tullave': '🔑 tu llave',
            'bancolombia': '🏦 Bancolombia',
            'bbva': '🏦 BBVA',
            'davivienda': '🏦 Davivienda'
        }
        return method_names.get(self.payment_method, f'🔧 {self.payment_method.title()}')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'multi_payment_id': self.multi_payment_id,
            'payment_method': self.payment_method,
            'payment_method_display': self.get_payment_method_display(),
            'amount': float(self.amount),
            'reference': self.reference,
            'bank_name': self.bank_name,
            'card_last_four': self.card_last_four,
            'phone_number': self.phone_number,
            'qr_code': self.qr_code,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<PaymentDetail {self.id}: {self.payment_method} ${self.amount}>'
