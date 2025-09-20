"""
Security Headers Middleware - Sistema POS O'Data
===============================================
Middleware para headers de seguridad enterprise.
"""

from flask import Flask, request, jsonify
import logging

logger = logging.getLogger(__name__)

class SecurityHeaders:
    """Middleware para headers de seguridad enterprise"""
    
    def __init__(self, app: Flask):
        self.app = app
        self._register_middleware()
    
    def _register_middleware(self):
        """Registrar middleware de headers de seguridad"""
        
        @self.app.after_request
        def add_security_headers(response):
            """Agregar headers de seguridad"""
            
            # Prevenir clickjacking
            response.headers['X-Frame-Options'] = 'DENY'
            
            # Prevenir MIME type sniffing
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            # Habilitar XSS protection
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # Referrer Policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Content Security Policy
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
            
            # Permissions Policy
            response.headers['Permissions-Policy'] = (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=()"
            )
            
            # Strict Transport Security (solo en HTTPS)
            if request.is_secure:
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Cache Control para APIs
            if request.path.startswith('/api/'):
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            
            return response
        
        @self.app.before_request
        def security_checks():
            """Verificaciones de seguridad antes del request"""
            
            # Verificar tamaño del request
            if request.content_length and request.content_length > 16 * 1024 * 1024:  # 16MB
                logger.warning(f"Request too large: {request.content_length} bytes", extra={
                    'request_id': getattr(request, 'request_id', None),
                    'remote_addr': request.remote_addr
                })
                return jsonify({
                    'error': {
                        'code': 'REQUEST_TOO_LARGE',
                        'message': 'Request size exceeds maximum allowed'
                    }
                }), 413
            
            # Verificar User-Agent
            if not request.user_agent or len(request.user_agent.string) > 500:
                logger.warning("Suspicious User-Agent", extra={
                    'request_id': getattr(request, 'request_id', None),
                    'remote_addr': request.remote_addr,
                    'user_agent': request.user_agent.string if request.user_agent else None
                })
            
            # Verificar Content-Type para requests con body
            if request.method in ['POST', 'PUT', 'PATCH'] and request.content_length:
                if not request.content_type or not request.content_type.startswith(('application/json', 'multipart/form-data')):
                    logger.warning(f"Invalid Content-Type: {request.content_type}", extra={
                        'request_id': getattr(request, 'request_id', None),
                        'remote_addr': request.remote_addr
                    })
                    return jsonify({
                        'error': {
                            'code': 'INVALID_CONTENT_TYPE',
                            'message': 'Content-Type must be application/json or multipart/form-data'
                        }
                    }), 400
