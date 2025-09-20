"""
Request Logger Middleware - Sistema POS O'Data
=============================================
Middleware para logging estructurado de requests.
"""

import logging
import time
import uuid
from flask import Flask, request, g
from datetime import datetime

logger = logging.getLogger(__name__)

class RequestLogger:
    """Middleware para logging estructurado de requests"""
    
    def __init__(self, app: Flask):
        self.app = app
        self._register_middleware()
    
    def _register_middleware(self):
        """Registrar middleware de logging"""
        
        @self.app.before_request
        def before_request():
            """Log antes del request"""
            g.request_id = str(uuid.uuid4())
            g.start_time = time.time()
            
            logger.info("Request started", extra={
                'request_id': g.request_id,
                'method': request.method,
                'url': request.url,
                'remote_addr': request.remote_addr,
                'user_agent': request.user_agent.string if request.user_agent else None,
                'content_type': request.content_type,
                'content_length': request.content_length
            })
        
        @self.app.after_request
        def after_request(response):
            """Log después del request"""
            if hasattr(g, 'request_id') and hasattr(g, 'start_time'):
                duration = time.time() - g.start_time
                
                logger.info("Request completed", extra={
                    'request_id': g.request_id,
                    'method': request.method,
                    'url': request.url,
                    'status_code': response.status_code,
                    'duration_ms': round(duration * 1000, 2),
                    'response_size': response.content_length
                })
                
                # Agregar request_id al header de respuesta
                response.headers['X-Request-ID'] = g.request_id
            
            return response
