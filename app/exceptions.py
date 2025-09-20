"""
Exception Hierarchy Enterprise - Sistema POS O'Data
==================================================
Jerarquía de excepciones profesional con contexto rico y manejo centralizado.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class POSException(Exception):
    """Excepción base del sistema POS"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "GENERIC_ERROR",
        context: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.status_code = status_code
        self.timestamp = datetime.utcnow()
        self.error_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir excepción a diccionario para respuesta JSON"""
        return {
            "error": {
                "id": self.error_id,
                "code": self.error_code,
                "message": self.message,
                "timestamp": self.timestamp.isoformat(),
                "context": self.context
            }
        }

class ValidationError(POSException):
    """Error de validación de datos"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        context = {}
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = str(value)
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context=context,
            status_code=400
        )

class BusinessLogicError(POSException):
    """Error de lógica de negocio"""
    
    def __init__(self, message: str, operation: str = None):
        context = {}
        if operation:
            context["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            context=context,
            status_code=422
        )

class NotFoundError(POSException):
    """Error de recurso no encontrado"""
    
    def __init__(self, resource_type: str, resource_id: Any = None):
        message = f"{resource_type} not found"
        if resource_id is not None:
            message += f" with ID: {resource_id}"
        
        context = {"resource_type": resource_type}
        if resource_id is not None:
            context["resource_id"] = str(resource_id)
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            context=context,
            status_code=404
        )

class InsufficientStockError(BusinessLogicError):
    """Error de stock insuficiente"""
    
    def __init__(self, product_id: int, requested: int, available: int):
        message = f"Insufficient stock for product {product_id}. Requested: {requested}, Available: {available}"
        context = {
            "product_id": product_id,
            "requested_quantity": requested,
            "available_quantity": available
        }
        
        super().__init__(
            message=message,
            operation="stock_check",
            context=context
        )

class AuthenticationError(POSException):
    """Error de autenticación"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401
        )

class AuthorizationError(POSException):
    """Error de autorización"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403
        )

class DatabaseError(POSException):
    """Error de base de datos"""
    
    def __init__(self, message: str, operation: str = None):
        context = {}
        if operation:
            context["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            context=context,
            status_code=500
        )

class ExternalServiceError(POSException):
    """Error de servicio externo"""
    
    def __init__(self, service_name: str, message: str):
        context = {"service": service_name}
        
        super().__init__(
            message=f"External service {service_name} error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            context=context,
            status_code=502
        )

class PaymentError(BusinessLogicError):
    """Error específico de procesamiento de pagos"""
    
    def __init__(self, message: str, payment_method: str = None, transaction_id: str = None):
        context = {}
        if payment_method:
            context["payment_method"] = payment_method
        if transaction_id:
            context["transaction_id"] = transaction_id
        
        super().__init__(
            message=message,
            operation="payment_processing"
        )
        self.context.update(context)