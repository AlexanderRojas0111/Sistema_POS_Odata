"""
Manejador de Errores Mejorado - Sistema POS O'Data
=================================================
Sistema robusto de manejo de errores con logging estructurado
"""

import logging
import traceback
from functools import wraps
from flask import request, jsonify, current_app
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow.exceptions import ValidationError
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Excepción base para errores de API"""
    
    def __init__(self, message, status_code=500, error_code=None, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"ERROR_{status_code}"
        self.details = details or {}

class ValidationAPIError(APIError):
    """Error de validación de datos"""
    
    def __init__(self, message, details=None):
        super().__init__(message, 400, "VALIDATION_ERROR", details)

class AuthenticationError(APIError):
    """Error de autenticación"""
    
    def __init__(self, message="No autorizado"):
        super().__init__(message, 401, "AUTHENTICATION_ERROR")

class AuthorizationError(APIError):
    """Error de autorización"""
    
    def __init__(self, message="Acceso denegado"):
        super().__init__(message, 403, "AUTHORIZATION_ERROR")

class NotFoundError(APIError):
    """Error de recurso no encontrado"""
    
    def __init__(self, message="Recurso no encontrado"):
        super().__init__(message, 404, "NOT_FOUND_ERROR")

class ConflictError(APIError):
    """Error de conflicto (ej: recurso duplicado)"""
    
    def __init__(self, message="Conflicto de datos"):
        super().__init__(message, 409, "CONFLICT_ERROR")

class RateLimitError(APIError):
    """Error de límite de velocidad"""
    
    def __init__(self, message="Límite de velocidad excedido"):
        super().__init__(message, 429, "RATE_LIMIT_ERROR")

class DatabaseError(APIError):
    """Error de base de datos"""
    
    def __init__(self, message="Error de base de datos"):
        super().__init__(message, 500, "DATABASE_ERROR")

class ExternalServiceError(APIError):
    """Error de servicio externo"""
    
    def __init__(self, message="Error de servicio externo"):
        super().__init__(message, 502, "EXTERNAL_SERVICE_ERROR")

def handle_error(error):
    """Manejador principal de errores"""
    
    # Log del error
    log_error(error)
    
    # Determinar tipo de error y respuesta
    if isinstance(error, APIError):
        return create_error_response(
            error.message,
            error.status_code,
            error.error_code,
            error.details
        )
    
    elif isinstance(error, ValidationError):
        return create_error_response(
            "Datos de entrada no válidos",
            400,
            "VALIDATION_ERROR",
            error.messages
        )
    
    elif isinstance(error, SQLAlchemyError):
        return handle_database_error(error)
    
    elif isinstance(error, HTTPException):
        return create_error_response(
            error.description or "Error HTTP",
            error.code,
            f"HTTP_{error.code}"
        )
    
    else:
        # Error no manejado
        return create_error_response(
            "Error interno del servidor",
            500,
            "INTERNAL_SERVER_ERROR"
        )

def handle_database_error(error):
    """Manejar errores específicos de base de datos"""
    
    if isinstance(error, IntegrityError):
        # Error de integridad (ej: clave duplicada)
        return create_error_response(
            "Conflicto de datos en la base de datos",
            409,
            "DATABASE_INTEGRITY_ERROR",
            {"detail": "El recurso ya existe o viola restricciones de integridad"}
        )
    
    else:
        # Otros errores de SQLAlchemy
        return create_error_response(
            "Error de base de datos",
            500,
            "DATABASE_ERROR"
        )

def create_error_response(message, status_code, error_code, details=None):
    """Crear respuesta de error estandarizada"""
    
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.path if request else None,
            "method": request.method if request else None
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    # Agregar información adicional en modo debug
    if current_app and current_app.debug:
        response["error"]["debug"] = {
            "traceback": traceback.format_exc()
        }
    
    return jsonify(response), status_code

def log_error(error):
    """Log estructurado de errores"""
    
    error_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "path": request.path if request else None,
        "method": request.method if request else None,
        "user_agent": request.headers.get('User-Agent') if request else None,
        "ip_address": request.remote_addr if request else None
    }
    
    # Agregar traceback para errores no manejados
    if not isinstance(error, APIError):
        error_data["traceback"] = traceback.format_exc()
    
    # Log según severidad
    if isinstance(error, (ValidationError, AuthenticationError, AuthorizationError)):
        logger.warning(f"Client error: {json.dumps(error_data)}")
    elif isinstance(error, (NotFoundError, ConflictError)):
        logger.info(f"Business logic error: {json.dumps(error_data)}")
    else:
        logger.error(f"Server error: {json.dumps(error_data)}")

def error_handler(f):
    """Decorator para manejo de errores en endpoints"""
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return handle_error(e)
    
    return decorated_function

def validate_and_handle_errors(schema=None):
    """Decorator combinado para validación y manejo de errores"""
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Validar datos si se proporciona esquema
                if schema:
                    data = request.get_json() or {}
                    validated_data = schema.load(data)
                    request.validated_data = validated_data
                
                return f(*args, **kwargs)
                
            except ValidationError as e:
                return handle_error(e)
            except Exception as e:
                return handle_error(e)
        
        return decorated_function
    return decorator

class ErrorHandlerEnhanced:
    """Manejador de errores mejorado para la aplicación"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar manejador de errores con la aplicación Flask"""
        
        # Registrar manejadores de errores
        app.register_error_handler(APIError, handle_error)
        app.register_error_handler(ValidationError, handle_error)
        app.register_error_handler(SQLAlchemyError, handle_error)
        app.register_error_handler(HTTPException, handle_error)
        app.register_error_handler(Exception, handle_error)
        
        # Configurar logging
        self._setup_logging(app)
    
    def _setup_logging(self, app):
        """Configurar logging estructurado"""
        
        if not app.debug:
            # Configurar logging para producción
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('logs/error.log'),
                    logging.StreamHandler()
                ]
            )
        else:
            # Configurar logging para desarrollo
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

# Instancia del manejador de errores
error_handler_enhanced = ErrorHandlerEnhanced()

# Funciones de conveniencia para lanzar errores
def raise_validation_error(message, details=None):
    """Lanzar error de validación"""
    raise ValidationAPIError(message, details)

def raise_not_found_error(message="Recurso no encontrado"):
    """Lanzar error de recurso no encontrado"""
    raise NotFoundError(message)

def raise_authentication_error(message="No autorizado"):
    """Lanzar error de autenticación"""
    raise AuthenticationError(message)

def raise_authorization_error(message="Acceso denegado"):
    """Lanzar error de autorización"""
    raise AuthorizationError(message)

def raise_conflict_error(message="Conflicto de datos"):
    """Lanzar error de conflicto"""
    raise ConflictError(message)

def raise_database_error(message="Error de base de datos"):
    """Lanzar error de base de datos"""
    raise DatabaseError(message)
