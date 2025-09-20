"""
Audit Logger - Sistema POS O'Data
================================
Sistema de auditoría enterprise para compliance y seguridad.
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from flask import request, g
import uuid

logger = logging.getLogger(__name__)

class AuditLogger:
    """Sistema de auditoría enterprise"""
    
    def __init__(self):
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        
        # Configurar handler para auditoría
        if not self.audit_logger.handlers:
            handler = logging.FileHandler('logs/audit.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.audit_logger.addHandler(handler)
    
    def log_authentication(self, user_id: int, success: bool, details: Dict[str, Any] = None):
        """Log de autenticación"""
        audit_data = {
            'event_type': 'AUTHENTICATION',
            'user_id': user_id,
            'success': success,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else None,
            'request_id': getattr(g, 'request_id', None),
            'details': details or {}
        }
        
        self.audit_logger.info(json.dumps(audit_data))
    
    def log_sale_creation(self, sale_id: int, user_id: int, amount: float, details: Dict[str, Any] = None):
        """Log de creación de venta"""
        audit_data = {
            'event_type': 'SALE_CREATED',
            'sale_id': sale_id,
            'user_id': user_id,
            'amount': amount,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else None,
            'request_id': getattr(g, 'request_id', None),
            'details': details or {}
        }
        
        self.audit_logger.info(json.dumps(audit_data))
    
    def log_sale_cancellation(self, sale_id: int, user_id: int, reason: str, details: Dict[str, Any] = None):
        """Log de cancelación de venta"""
        audit_data = {
            'event_type': 'SALE_CANCELLED',
            'sale_id': sale_id,
            'user_id': user_id,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else None,
            'request_id': getattr(g, 'request_id', None),
            'details': details or {}
        }
        
        self.audit_logger.info(json.dumps(audit_data))
    
    def log_product_creation(self, product_id: int, user_id: int, details: Dict[str, Any] = None):
        """Log de creación de producto"""
        audit_data = {
            'event_type': 'PRODUCT_CREATED',
            'product_id': product_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else None,
            'request_id': getattr(g, 'request_id', None),
            'details': details or {}
        }
        
        self.audit_logger.info(json.dumps(audit_data))
    
    def log_stock_adjustment(self, product_id: int, user_id: int, old_stock: int, new_stock: int, reason: str):
        """Log de ajuste de stock"""
        audit_data = {
            'event_type': 'STOCK_ADJUSTED',
            'product_id': product_id,
            'user_id': user_id,
            'old_stock': old_stock,
            'new_stock': new_stock,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else None,
            'request_id': getattr(g, 'request_id', None)
        }
        
        self.audit_logger.info(json.dumps(audit_data))
    
    def log_security_event(self, event_type: str, severity: str, details: Dict[str, Any] = None):
        """Log de evento de seguridad"""
        audit_data = {
            'event_type': f'SECURITY_{event_type}',
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else None,
            'request_id': getattr(g, 'request_id', None),
            'details': details or {}
        }
        
        if severity == 'HIGH':
            self.audit_logger.error(json.dumps(audit_data))
        else:
            self.audit_logger.warning(json.dumps(audit_data))
    
    def log_data_access(self, user_id: int, resource_type: str, resource_id: int, action: str):
        """Log de acceso a datos"""
        audit_data = {
            'event_type': 'DATA_ACCESS',
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else None,
            'request_id': getattr(g, 'request_id', None)
        }
        
        self.audit_logger.info(json.dumps(audit_data))
    
    def log_system_event(self, event_type: str, details: Dict[str, Any] = None):
        """Log de evento del sistema"""
        audit_data = {
            'event_type': f'SYSTEM_{event_type}',
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string if request.user_agent else None,
            'request_id': getattr(g, 'request_id', None),
            'details': details or {}
        }
        
        self.audit_logger.info(json.dumps(audit_data))
