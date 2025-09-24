"""
Configuración de Seguridad Empresarial
Hardening y configuraciones de seguridad avanzadas
"""

import os
import secrets
import hashlib
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from flask import Flask, request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

logger = logging.getLogger('security')

class SecurityConfig:
    """Configuración centralizada de seguridad"""
    
    # Headers de seguridad obligatorios
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'"
        ),
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }
    
    # Configuración de rate limiting por endpoint
    RATE_LIMITS = {
        'auth_login': '5 per minute',
        'auth_refresh': '10 per minute',
        'api_general': '100 per minute',
        'search': '50 per minute',
        'upload': '5 per minute'
    }
    
    # IPs y User-Agents bloqueados
    BLOCKED_IPS = set()
    BLOCKED_USER_AGENTS = [
        'sqlmap', 'nikto', 'nmap', 'masscan',
        'bot', 'crawler', 'spider'
    ]
    
    # Patrones sospechosos en URLs
    SUSPICIOUS_PATTERNS = [
        'admin', 'phpmyadmin', 'wp-admin', 'wp-login',
        '.env', '.git', 'config', 'backup'
    ]

class SecurityMiddleware:
    """Middleware de seguridad para requests"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.setup_middleware()
    
    def setup_middleware(self):
        """Configurar middleware de seguridad"""
        
        @self.app.before_request
        def security_checks():
            """Verificaciones de seguridad antes de cada request"""
            
            # Generar ID único para el request
            g.request_id = f"{int(datetime.utcnow().timestamp())}-{secrets.token_hex(4)}"
            g.request_start_time = datetime.utcnow()
            
            # Verificar IP bloqueada
            if request.remote_addr in SecurityConfig.BLOCKED_IPS:
                logger.warning(f"Request desde IP bloqueada: {request.remote_addr}")
                return {'error': 'Access denied'}, 403
            
            # Verificar User-Agent sospechoso
            user_agent = request.headers.get('User-Agent', '').lower()
            for blocked_agent in SecurityConfig.BLOCKED_USER_AGENTS:
                if blocked_agent in user_agent:
                    logger.warning(f"Request con User-Agent bloqueado: {user_agent}")
                    return {'error': 'Access denied'}, 403
            
            # Verificar patrones sospechosos en URL
            url_path = request.path.lower()
            for pattern in SecurityConfig.SUSPICIOUS_PATTERNS:
                if pattern in url_path:
                    logger.warning(f"Request con patrón sospechoso: {request.path}")
                    return {'error': 'Not found'}, 404
            
            # Verificar tamaño de payload
            max_content_length = self.app.config.get('MAX_CONTENT_LENGTH', 8 * 1024 * 1024)
            if request.content_length and request.content_length > max_content_length:
                logger.warning(f"Request con payload muy grande: {request.content_length}")
                return {'error': 'Payload too large'}, 413
        
        @self.app.after_request
        def security_headers(response):
            """Agregar headers de seguridad a todas las respuestas"""
            
            # Headers de seguridad
            for header, value in SecurityConfig.SECURITY_HEADERS.items():
                response.headers[header] = value
            
            # Header personalizado con información del servidor
            response.headers['X-API-Version'] = self.app.config.get('APP_VERSION', '2.0.2')
            response.headers['X-Request-ID'] = getattr(g, 'request_id', 'unknown')
            
            # Remover headers que revelan información del servidor
            response.headers.pop('Server', None)
            response.headers.pop('X-Powered-By', None)
            
            return response

class RateLimitingConfig:
    """Configuración avanzada de rate limiting"""
    
    @staticmethod
    def get_key_func():
        """Función para identificar clientes para rate limiting"""
        
        # Usar IP + User-Agent como identificador
        ip = request.remote_addr
        user_agent_hash = hashlib.md5(
            request.headers.get('User-Agent', '').encode()
        ).hexdigest()[:8]
        
        # Si hay usuario autenticado, usar su ID
        user_id = getattr(g, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        
        return f"ip:{ip}:ua:{user_agent_hash}"
    
    @staticmethod
    def get_rate_limit_for_endpoint():
        """Obtener límite específico para el endpoint actual"""
        
        endpoint = request.endpoint
        if not endpoint:
            return SecurityConfig.RATE_LIMITS['api_general']
        
        # Límites específicos por endpoint
        if 'auth.login' in endpoint:
            return SecurityConfig.RATE_LIMITS['auth_login']
        elif 'auth.refresh' in endpoint:
            return SecurityConfig.RATE_LIMITS['auth_refresh']
        elif 'search' in endpoint:
            return SecurityConfig.RATE_LIMITS['search']
        elif 'upload' in endpoint:
            return SecurityConfig.RATE_LIMITS['upload']
        else:
            return SecurityConfig.RATE_LIMITS['api_general']

class InputSanitizer:
    """Sanitizador avanzado de entrada"""
    
    @staticmethod
    def sanitize_json_payload(data: Dict) -> Dict:
        """Sanitizar payload JSON completo"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            # Sanitizar clave
            clean_key = InputSanitizer._sanitize_string(str(key))
            
            # Sanitizar valor según tipo
            if isinstance(value, str):
                clean_value = InputSanitizer._sanitize_string(value)
            elif isinstance(value, dict):
                clean_value = InputSanitizer.sanitize_json_payload(value)
            elif isinstance(value, list):
                clean_value = [
                    InputSanitizer._sanitize_string(item) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                clean_value = value
            
            sanitized[clean_key] = clean_value
        
        return sanitized
    
    @staticmethod
    def _sanitize_string(value: str) -> str:
        """Sanitizar string individual"""
        if not isinstance(value, str):
            return str(value)
        
        # Remover caracteres de control
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n\r')
        
        # Limitar longitud
        max_length = 10000  # Límite razonable
        if len(value) > max_length:
            value = value[:max_length]
            logger.warning(f"String truncado por exceder longitud máxima: {max_length}")
        
        return value.strip()

class AuditLogger:
    """Logger de auditoría para eventos críticos"""
    
    @staticmethod
    def log_data_access(entity_type: str, entity_id: str, operation: str, user_id: str = None):
        """Log de acceso a datos sensibles"""
        LoggerUtils.log_security_event(
            'data_access',
            {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'operation': operation,
                'user_id': user_id or getattr(g, 'user_id', 'anonymous'),
                'ip_address': request.remote_addr,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def log_privilege_escalation(user_id: str, old_role: str, new_role: str, admin_user_id: str):
        """Log de cambio de privilegios"""
        LoggerUtils.log_security_event(
            'privilege_escalation',
            {
                'target_user_id': user_id,
                'old_role': old_role,
                'new_role': new_role,
                'admin_user_id': admin_user_id,
                'ip_address': request.remote_addr,
                'timestamp': datetime.utcnow().isoformat()
            },
            level='WARNING'
        )
    
    @staticmethod
    def log_configuration_change(setting: str, old_value: str, new_value: str, user_id: str):
        """Log de cambio de configuración"""
        LoggerUtils.log_security_event(
            'configuration_change',
            {
                'setting': setting,
                'old_value': old_value,
                'new_value': new_value,
                'user_id': user_id,
                'ip_address': request.remote_addr,
                'timestamp': datetime.utcnow().isoformat()
            },
            level='INFO'
        )

def setup_advanced_security(app: Flask):
    """Configurar seguridad avanzada para la aplicación"""
    
    # Middleware de seguridad
    SecurityMiddleware(app)
    
    # Configurar rate limiting avanzado
    if app.config.get('RATELIMIT_ENABLED', False):
        limiter = Limiter(
            app=app,
            key_func=RateLimitingConfig.get_key_func,
            default_limits=[SecurityConfig.RATE_LIMITS['api_general']],
            storage_uri=app.config.get('RATELIMIT_STORAGE_URL')
        )
        app.limiter = limiter
        
        # Rate limiting dinámico por endpoint
        @limiter.request_filter
        def rate_limit_filter():
            """Filtro para aplicar rate limiting dinámico"""
            # Eximir health checks
            if request.endpoint in ['health_check', 'ai_health']:
                return False
            return True
    
    # Configurar CSRF protection (si es necesario)
    if app.config.get('CSRF_ENABLED', False):
        from flask_wtf.csrf import CSRFProtect
        csrf = CSRFProtect(app)
    
    # Configurar session security
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Strict',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
    )
    
    logger.info("Configuración de seguridad avanzada aplicada")

# Decoradores de seguridad
def require_https(func):
    """Decorador para requerir HTTPS"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.is_secure and not current_app.debug:
            return {'error': 'HTTPS required'}, 400
        return func(*args, **kwargs)
    return wrapper

def audit_data_access(entity_type: str):
    """Decorador para auditar acceso a datos"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obtener ID de entidad de los argumentos
            entity_id = kwargs.get('id') or (args[0] if args else 'unknown')
            
            # Log de acceso
            AuditLogger.log_data_access(
                entity_type=entity_type,
                entity_id=str(entity_id),
                operation=func.__name__,
                user_id=getattr(g, 'user_id', None)
            )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_permissions(required_permissions: List[str]):
    """Decorador para validar permisos"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_permissions = getattr(g, 'user_permissions', [])
            
            # Verificar si el usuario tiene al menos uno de los permisos requeridos
            if not any(perm in user_permissions for perm in required_permissions):
                logger.warning(
                    f"Acceso denegado - Permisos insuficientes",
                    extra={
                        'required_permissions': required_permissions,
                        'user_permissions': user_permissions,
                        'user_id': getattr(g, 'user_id', None),
                        'endpoint': request.endpoint
                    }
                )
                return {'error': 'Permisos insuficientes'}, 403
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
