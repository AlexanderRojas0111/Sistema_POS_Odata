"""
Support Document Model - Sistema POS Sabrositas
==============================================
Modelo para documentos soporte electrónicos.
"""

from app import db
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal
import uuid

class SupportDocument(db.Model):
    """Modelo de documento soporte electrónico"""
    
    __tablename__ = 'support_documents'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    document_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Información fiscal
    company_nit = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    customer_nit = db.Column(db.String(20), nullable=True)
    customer_name = db.Column(db.String(200), nullable=False)
    
    # Totales
    subtotal = db.Column(db.Numeric(12, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    
    # Tipo de documento
    document_type = db.Column(db.String(20), default='support')  # support, adjustment, credit_note
    
    # Estado fiscal
    fiscal_status = db.Column(db.String(20), default='pending')
    dian_response = db.Column(db.Text, nullable=True)
    cude = db.Column(db.String(100), nullable=True)  # Código Único de Documento Electrónico
    
    # Referencias
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('electronic_invoices.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, user_id: int, **kwargs):
        """Constructor con validaciones"""
        self.user_id = user_id
        
        # Generar número de documento
        self.document_number = self._generate_document_number()
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _generate_document_number(self) -> str:
        """Generar número de documento único"""
        # Formato: DS + Año + Mes + Secuencial (ej: DS2025010001)
        now = datetime.utcnow()
        prefix = f"DS{now.year}{now.month:02d}"
        
        # Buscar último número de la serie
        last_doc = SupportDocument.query.filter(
            SupportDocument.document_number.like(f"{prefix}%")
        ).order_by(SupportDocument.document_number.desc()).first()
        
        if last_doc:
            last_number = int(last_doc.document_number[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'document_number': self.document_number,
            'company_nit': self.company_nit,
            'company_name': self.company_name,
            'customer_nit': self.customer_nit,
            'customer_name': self.customer_name,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount),
            'document_type': self.document_type,
            'fiscal_status': self.fiscal_status,
            'cude': self.cude,
            'sale_id': self.sale_id,
            'invoice_id': self.invoice_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None
        }
    
    def __repr__(self) -> str:
        return f'<SupportDocument {self.document_number}>'
