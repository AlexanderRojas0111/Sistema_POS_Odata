"""
Advanced Rate Limiter - Sistema POS O'Data
==========================================
Rate limiting avanzado con diferentes límites por endpoint y usuario.
"""

from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

logger = logging.getLogger(__name__)

class AdvancedRateLimiter:
    """Rate limiter avanzado con configuración enterprise"""
    
    def __init__(self, app: Flask):
        self.app = app
        # No crear limiter aquí, usar el existente
        self._configure_rate_limits()
    
    def _get_rate_limit_key(self):
        """Obtener clave para rate limiting"""
        # Usar IP + User-Agent para mejor identificación
        user_agent = request.user_agent.string if request.user_agent else 'unknown'
        return f"{get_remote_address()}:{hash(user_agent)}"
    
    def _configure_rate_limits(self):
        """Configurar límites específicos por endpoint"""
        # Obtener el limiter existente de la app
        self.limiter = self.app.extensions.get('limiter')
        
        if not self.limiter:
            logger.warning("No limiter found in app extensions")
            return
    
    def apply_rate_limits(self):
        """Aplicar rate limits a endpoints específicos"""
        
        # Decoradores para diferentes tipos de endpoints
        self.login_limit = self.limiter.limit("5 per minute")
        self.creation_limit = self.limiter.limit("20 per minute")
        self.read_limit = self.limiter.limit("200 per minute")
        self.critical_limit = self.limiter.limit("10 per minute")
        self.stats_limit = self.limiter.limit("50 per minute")
        
        # Rate limiting global por IP
        self.global_limit = self.limiter.limit("1000 per hour")
    
    def get_rate_limit_info(self, endpoint: str) -> dict:
        """Obtener información de rate limiting para un endpoint"""
        limits = {
            'login': {'limit': '5 per minute', 'description': 'Anti brute force'},
            'creation': {'limit': '20 per minute', 'description': 'Resource creation'},
            'read': {'limit': '200 per minute', 'description': 'Data reading'},
            'critical': {'limit': '10 per minute', 'description': 'Critical operations'},
            'stats': {'limit': '50 per minute', 'description': 'Statistics and reports'},
            'global': {'limit': '1000 per hour', 'description': 'Global per IP limit'}
        }
        
        return limits.get(endpoint, limits['global'])
