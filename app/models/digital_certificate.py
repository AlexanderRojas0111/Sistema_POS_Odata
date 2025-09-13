"""
Digital Certificate Model - Sistema POS Sabrositas
=================================================
Modelo para gestión de certificados digitales.
"""

from app import db
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import uuid
import base64

class DigitalCertificate(db.Model):
    """Modelo de certificado digital"""
    
    __tablename__ = 'digital_certificates'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    certificate_name = db.Column(db.String(100), nullable=False)
    
    # Información del certificado
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    issuer = db.Column(db.String(500), nullable=False)
    
    # Fechas de validez
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_until = db.Column(db.DateTime, nullable=False)
    
    # Estado
    status = db.Column(db.String(20), default='active')  # active, expired, revoked
    is_default = db.Column(db.Boolean, default=False)
    
    # Archivos
    certificate_file = db.Column(db.LargeBinary, nullable=False)
    private_key_file = db.Column(db.LargeBinary, nullable=True)
    password = db.Column(db.String(255), nullable=True)  # Encriptado
    
    # Información de la empresa
    company_nit = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, **kwargs):
        """Constructor con validaciones"""
        # Asignar campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def is_valid(self) -> bool:
        """Verificar si el certificado es válido"""
        now = datetime.utcnow()
        return (
            self.status == 'active' and
            now >= self.valid_from and
            now <= self.valid_until
        )
    
    def is_expired(self) -> bool:
        """Verificar si el certificado está expirado"""
        return datetime.utcnow() > self.valid_until
    
    def days_until_expiry(self) -> int:
        """Días hasta la expiración"""
        delta = self.valid_until - datetime.utcnow()
        return delta.days
    
    def to_dict(self, include_files: bool = False) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        data = {
            'id': self.id,
            'uuid': self.uuid,
            'certificate_name': self.certificate_name,
            'serial_number': self.serial_number,
            'subject': self.subject,
            'issuer': self.issuer,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'status': self.status,
            'is_default': self.is_default,
            'company_nit': self.company_nit,
            'company_name': self.company_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'is_valid': self.is_valid(),
            'is_expired': self.is_expired(),
            'days_until_expiry': self.days_until_expiry()
        }
        
        if include_files and self.certificate_file:
            data['certificate_file'] = base64.b64encode(self.certificate_file).decode('utf-8')
        
        return data
    
    def __repr__(self) -> str:
        return f'<DigitalCertificate {self.certificate_name}: {self.serial_number}>'

class CertificateUsage(db.Model):
    """Modelo de uso de certificados"""
    
    __tablename__ = 'certificate_usage'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.Integer, db.ForeignKey('digital_certificates.id'), nullable=False)
    
    # Información del uso
    document_type = db.Column(db.String(20), nullable=False)  # invoice, support_document
    document_id = db.Column(db.Integer, nullable=False)
    document_number = db.Column(db.String(50), nullable=False)
    
    # Resultado
    success = db.Column(db.Boolean, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    
    # Timestamps
    used_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, certificate_id: int, **kwargs):
        """Constructor con validaciones"""
        self.certificate_id = certificate_id
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'id': self.id,
            'certificate_id': self.certificate_id,
            'document_type': self.document_type,
            'document_id': self.document_id,
            'document_number': self.document_number,
            'success': self.success,
            'error_message': self.error_message,
            'used_at': self.used_at.isoformat() if self.used_at else None
        }
    
    def __repr__(self) -> str:
        return f'<CertificateUsage {self.id}: {self.document_type} #{self.document_number}>'
