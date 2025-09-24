"""
Sistema de Manejo de Excepciones Empresariales
Implementación de manejo robusto y estandarizado de errores
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from flask import jsonify, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

class POSBaseException(Exception):
    """Excepción base del sistema POS"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "GENERIC_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.user_message = user_message or "Ha ocurrido un error interno"
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convertir excepción a diccionario para respuesta JSON"""
        return {
            'success': False,
            'error': {
                'code': self.error_code,
                'message': self.user_message,
                'technical_message': self.message,
                'details': self.details,
                'timestamp': self.timestamp
            }
        }

class ValidationException(POSBaseException):
    """Excepción para errores de validación de datos"""
    
    def __init__(self, message: str, field: str = None, value: Any = None):
        details = {}
        if field:
            details['field'] = field
        if value is not None:
            details['invalid_value'] = str(value)
            
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details,
            user_message="Los datos proporcionados no son válidos"
        )

class AuthenticationException(POSBaseException):
    """Excepción para errores de autenticación"""
    
    def __init__(self, message: str = "Credenciales inválidas"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            user_message="Credenciales de acceso inválidas"
        )

class AuthorizationException(POSBaseException):
    """Excepción para errores de autorización"""
    
    def __init__(self, message: str = "Acceso no autorizado", required_permission: str = None):
        details = {}
        if required_permission:
            details['required_permission'] = required_permission
            
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details,
            user_message="No tiene permisos para realizar esta acción"
        )

class ResourceNotFoundException(POSBaseException):
    """Excepción para recursos no encontrados"""
    
    def __init__(self, resource_type: str, resource_id: Any = None):
        message = f"{resource_type} no encontrado"
        if resource_id:
            message += f" con ID: {resource_id}"
            
        super().__init__(
            message=message,
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={'resource_type': resource_type, 'resource_id': resource_id},
            user_message=f"El {resource_type.lower()} solicitado no existe"
        )

class BusinessLogicException(POSBaseException):
    """Excepción para errores de lógica de negocio"""
    
    def __init__(self, message: str, business_rule: str = None):
        details = {}
        if business_rule:
            details['business_rule'] = business_rule
            
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            status_code=422,
            details=details,
            user_message="La operación no se puede completar debido a reglas de negocio"
        )

class ExternalServiceException(POSBaseException):
    """Excepción para errores de servicios externos"""
    
    def __init__(self, service_name: str, message: str = None):
        message = message or f"Error en servicio externo: {service_name}"
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=503,
            details={'service_name': service_name},
            user_message="Servicio temporalmente no disponible. Intente más tarde."
        )

class RateLimitException(POSBaseException):
    """Excepción para límite de tasa excedido"""
    
    def __init__(self, limit: int = None, window: int = None):
        details = {}
        if limit:
            details['limit'] = limit
        if window:
            details['window_seconds'] = window
            
        super().__init__(
            message="Rate limit exceeded",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details,
            user_message="Demasiadas solicitudes. Intente más tarde."
        )

class DatabaseException(POSBaseException):
    """Excepción para errores de base de datos"""
    
    def __init__(self, message: str, operation: str = None):
        details = {}
        if operation:
            details['database_operation'] = operation
            
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details,
            user_message="Error interno de base de datos"
        )

# Manejador global de excepciones
def register_error_handlers(app):
    """Registrar manejadores de errores globales"""
    
    @app.errorhandler(POSBaseException)
    def handle_pos_exception(error: POSBaseException):
        """Manejar excepciones del sistema POS"""
        
        # Log del error
        logger.error(
            f"POS Exception: {error.error_code} - {error.message}",
            extra={
                'error_code': error.error_code,
                'status_code': error.status_code,
                'details': error.details,
                'request_id': getattr(request, 'id', None),
                'user_id': getattr(request, 'user_id', None),
                'endpoint': request.endpoint,
                'method': request.method,
                'url': request.url
            }
        )
        
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Manejar errores de validación de Marshmallow"""
        validation_exception = ValidationException(
            message=f"Validation failed: {error.messages}",
            details={'validation_errors': error.messages}
        )
        return handle_pos_exception(validation_exception)
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Manejar excepciones HTTP estándar"""
        
        pos_exception = POSBaseException(
            message=error.description or str(error),
            error_code=f"HTTP_{error.code}",
            status_code=error.code,
            user_message=get_user_friendly_message(error.code)
        )
        return handle_pos_exception(pos_exception)
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        """Manejar excepciones no capturadas"""
        
        # Log completo del error
        logger.error(
            f"Unhandled exception: {str(error)}",
            extra={
                'exception_type': type(error).__name__,
                'traceback': traceback.format_exc(),
                'request_id': getattr(request, 'id', None),
                'endpoint': request.endpoint,
                'method': request.method,
                'url': request.url
            }
        )
        
        pos_exception = POSBaseException(
            message=str(error),
            error_code="INTERNAL_SERVER_ERROR",
            status_code=500,
            user_message="Ha ocurrido un error interno inesperado"
        )
        return handle_pos_exception(pos_exception)

def get_user_friendly_message(status_code: int) -> str:
    """Obtener mensaje amigable para códigos de estado HTTP"""
    
    messages = {
        400: "Solicitud inválida",
        401: "Acceso no autorizado",
        403: "Acceso prohibido",
        404: "Recurso no encontrado",
        405: "Método no permitido",
        409: "Conflicto en la operación",
        422: "Datos no procesables",
        429: "Demasiadas solicitudes",
        500: "Error interno del servidor",
        502: "Servicio no disponible",
        503: "Servicio temporalmente no disponible",
        504: "Tiempo de espera agotado"
    }
    
    return messages.get(status_code, "Error en el servidor")

# Decorador para manejo de errores en endpoints
def handle_errors(func):
    """Decorador para manejo automático de errores en endpoints"""
    
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except POSBaseException:
            # Re-raise POS exceptions para que sean manejadas por el handler global
            raise
        except ValueError as e:
            raise ValidationException(f"Valor inválido: {str(e)}")
        except KeyError as e:
            raise ValidationException(f"Campo requerido faltante: {str(e)}")
        except Exception as e:
            # Log y re-raise para manejo global
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise
    
    return wrapper

# Utilidades para auditoría y logging
class ErrorAuditor:
    """Auditor de errores para análisis y métricas"""
    
    @staticmethod
    def log_error_metrics(error: POSBaseException):
        """Registrar métricas de error para análisis"""
        
        # Aquí se integraría con sistemas de métricas como Prometheus
        metrics_data = {
            'error_code': error.error_code,
            'status_code': error.status_code,
            'timestamp': error.timestamp,
            'endpoint': getattr(request, 'endpoint', None),
            'user_id': getattr(request, 'user_id', None)
        }
        
        # Log para análisis posterior
        logger.info("Error metrics", extra=metrics_data)
    
    @staticmethod
    def should_alert(error: POSBaseException) -> bool:
        """Determinar si un error requiere alerta inmediata"""
        
        critical_errors = [
            "DATABASE_ERROR",
            "EXTERNAL_SERVICE_ERROR",
            "INTERNAL_SERVER_ERROR"
        ]
        
        return error.error_code in critical_errors or error.status_code >= 500
