"""
Sistema de Logging Centralizado y Estructurado
Configuración empresarial de logging con múltiples handlers y formatters
"""

import os
import sys
import json
import logging
import logging.config
from datetime import datetime
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from flask import request, g, has_request_context
from pythonjsonlogger import jsonlogger

class ContextFilter(logging.Filter):
    """Filtro para agregar contexto de request a los logs"""
    
    def filter(self, record):
        if has_request_context():
            # Información del request
            record.request_id = getattr(g, 'request_id', None)
            record.user_id = getattr(g, 'user_id', None)
            record.username = getattr(g, 'username', None)
            record.endpoint = request.endpoint
            record.method = request.method
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.user_agent = request.headers.get('User-Agent', 'Unknown')
            
            # Headers importantes (sin datos sensibles)
            record.content_type = request.content_type
            record.content_length = request.content_length
        else:
            # Valores por defecto cuando no hay contexto de request
            record.request_id = None
            record.user_id = None
            record.username = None
            record.endpoint = None
            record.method = None
            record.url = None
            record.remote_addr = None
            record.user_agent = None
            record.content_type = None
            record.content_length = None
        
        # Información del sistema
        record.hostname = os.uname().nodename if hasattr(os, 'uname') else 'unknown'
        record.process_id = os.getpid()
        record.thread_id = record.thread
        
        return True

class SecurityFilter(logging.Filter):
    """Filtro para detectar y marcar eventos de seguridad"""
    
    SECURITY_KEYWORDS = [
        'authentication', 'authorization', 'login', 'logout',
        'permission', 'access', 'security', 'attack', 'injection',
        'xss', 'csrf', 'unauthorized', 'forbidden', 'suspicious'
    ]
    
    def filter(self, record):
        # Detectar eventos de seguridad
        message_lower = record.getMessage().lower()
        record.is_security_event = any(
            keyword in message_lower for keyword in self.SECURITY_KEYWORDS
        )
        
        # Marcar nivel de severidad de seguridad
        if record.is_security_event:
            if record.levelno >= logging.ERROR:
                record.security_level = 'CRITICAL'
            elif record.levelno >= logging.WARNING:
                record.security_level = 'HIGH'
            else:
                record.security_level = 'MEDIUM'
        else:
            record.security_level = None
        
        return True

class PerformanceFilter(logging.Filter):
    """Filtro para métricas de performance"""
    
    def filter(self, record):
        if hasattr(record, 'duration'):
            # Clasificar performance
            duration = record.duration
            if duration > 5.0:
                record.performance_level = 'SLOW'
            elif duration > 1.0:
                record.performance_level = 'MODERATE'
            else:
                record.performance_level = 'FAST'
        else:
            record.performance_level = None
        
        return True

class CustomJSONFormatter(jsonlogger.JsonFormatter):
    """Formatter JSON personalizado para logs estructurados"""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Campos estándar
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Contexto de aplicación
        log_record['service'] = 'pos-odata'
        log_record['version'] = os.getenv('APP_VERSION', '2.0.2')
        log_record['environment'] = os.getenv('FLASK_ENV', 'development')
        
        # Limpiar campos None
        log_record = {k: v for k, v in log_record.items() if v is not None}

class ColoredFormatter(logging.Formatter):
    """Formatter con colores para desarrollo"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Aplicar color al nivel
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)

def setup_logging(app):
    """Configurar sistema de logging para la aplicación"""
    
    # Crear directorios de logs
    log_dir = app.config.get('LOG_DIR', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configuración base
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_format = app.config.get('LOG_FORMAT', 'json')  # 'json' o 'text'
    
    # Configuración de logging
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': CustomJSONFormatter,
                'format': '%(timestamp)s %(level)s %(message)s'
            },
            'detailed': {
                'format': (
                    '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - '
                    '%(message)s [%(request_id)s|%(user_id)s]'
                )
            },
            'colored': {
                '()': ColoredFormatter,
                'format': (
                    '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - '
                    '%(message)s'
                )
            }
        },
        'filters': {
            'context_filter': {
                '()': ContextFilter
            },
            'security_filter': {
                '()': SecurityFilter
            },
            'performance_filter': {
                '()': PerformanceFilter
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'colored' if app.debug else 'json',
                'filters': ['context_filter', 'security_filter'],
                'stream': sys.stdout
            },
            'file_app': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'app.log'),
                'maxBytes': 50 * 1024 * 1024,  # 50MB
                'backupCount': 10,
                'formatter': 'json',
                'filters': ['context_filter', 'security_filter', 'performance_filter']
            },
            'file_security': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(log_dir, 'security.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 30,
                'formatter': 'json',
                'filters': ['context_filter', 'security_filter']
            },
            'file_performance': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'performance.log'),
                'maxBytes': 25 * 1024 * 1024,  # 25MB
                'backupCount': 5,
                'formatter': 'json',
                'filters': ['context_filter', 'performance_filter']
            },
            'file_error': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(log_dir, 'error.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 30,
                'formatter': 'json',
                'filters': ['context_filter', 'security_filter'],
                'level': 'ERROR'
            }
        },
        'loggers': {
            # Logger de aplicación principal
            'app': {
                'level': log_level,
                'handlers': ['console', 'file_app'],
                'propagate': False
            },
            # Logger de seguridad
            'security': {
                'level': 'INFO',
                'handlers': ['console', 'file_security', 'file_error'],
                'propagate': False
            },
            # Logger de performance
            'performance': {
                'level': 'INFO',
                'handlers': ['file_performance'],
                'propagate': False
            },
            # Logger de base de datos
            'sqlalchemy': {
                'level': 'WARNING',
                'handlers': ['file_app'],
                'propagate': False
            },
            # Logger de requests HTTP
            'werkzeug': {
                'level': 'WARNING',
                'handlers': ['file_app'],
                'propagate': False
            },
            # Logger raíz
            '': {
                'level': log_level,
                'handlers': ['console', 'file_app', 'file_error']
            }
        }
    }
    
    # Aplicar configuración
    logging.config.dictConfig(logging_config)
    
    # Configurar logger de Flask
    app.logger.handlers.clear()
    app.logger.addHandler(logging.getLogger('app').handlers[0])
    app.logger.setLevel(getattr(logging, log_level.upper()))
    
    app.logger.info(f"Logging configurado - Nivel: {log_level}, Formato: {log_format}")

# Utilidades de logging
class LoggerUtils:
    """Utilidades para logging estructurado"""
    
    @staticmethod
    def log_request_start():
        """Log de inicio de request"""
        if has_request_context():
            logger = logging.getLogger('app')
            logger.info(
                "Request iniciado",
                extra={
                    'event_type': 'request_start',
                    'method': request.method,
                    'endpoint': request.endpoint,
                    'url': request.url,
                    'content_type': request.content_type,
                    'content_length': request.content_length
                }
            )
    
    @staticmethod
    def log_request_end(status_code: int, duration: float):
        """Log de fin de request"""
        if has_request_context():
            logger = logging.getLogger('performance')
            logger.info(
                "Request completado",
                extra={
                    'event_type': 'request_end',
                    'status_code': status_code,
                    'duration': duration,
                    'method': request.method,
                    'endpoint': request.endpoint
                }
            )
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict[str, Any], level: str = 'WARNING'):
        """Log de evento de seguridad"""
        logger = logging.getLogger('security')
        log_level = getattr(logging, level.upper())
        
        logger.log(
            log_level,
            f"Evento de seguridad: {event_type}",
            extra={
                'event_type': 'security_event',
                'security_event_type': event_type,
                'details': details,
                'is_security_event': True
            }
        )
    
    @staticmethod
    def log_business_event(event_type: str, entity_type: str, entity_id: Any, details: Dict[str, Any] = None):
        """Log de evento de negocio"""
        logger = logging.getLogger('app')
        
        logger.info(
            f"Evento de negocio: {event_type} - {entity_type}",
            extra={
                'event_type': 'business_event',
                'business_event_type': event_type,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'details': details or {}
            }
        )
    
    @staticmethod
    def log_database_operation(operation: str, table: str, duration: float, affected_rows: int = None):
        """Log de operación de base de datos"""
        logger = logging.getLogger('performance')
        
        logger.info(
            f"Operación DB: {operation} en {table}",
            extra={
                'event_type': 'database_operation',
                'operation': operation,
                'table': table,
                'duration': duration,
                'affected_rows': affected_rows
            }
        )

# Decorador para logging automático
def log_execution_time(logger_name: str = 'performance'):
    """Decorador para medir y loggear tiempo de ejecución"""
    
    def decorator(func):
        from functools import wraps
        import time
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger = logging.getLogger(logger_name)
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(
                    f"Función {func.__name__} ejecutada",
                    extra={
                        'event_type': 'function_execution',
                        'function_name': func.__name__,
                        'duration': duration,
                        'status': 'success'
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(
                    f"Error en función {func.__name__}: {str(e)}",
                    extra={
                        'event_type': 'function_execution',
                        'function_name': func.__name__,
                        'duration': duration,
                        'status': 'error',
                        'error': str(e)
                    }
                )
                raise
        
        return wrapper
    return decorator

# Middleware para logging automático de requests
def setup_request_logging(app):
    """Configurar logging automático de requests"""
    
    @app.before_request
    def log_request_info():
        LoggerUtils.log_request_start()
    
    @app.after_request
    def log_request_response(response):
        # Calcular duración si está disponible
        duration = getattr(g, 'request_duration', None)
        if duration:
            LoggerUtils.log_request_end(response.status_code, duration)
        
        return response
