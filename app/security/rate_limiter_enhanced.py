"""
Rate Limiter Enhanced - Sistema POS O'Data
=========================================
Sistema profesional de rate limiting con Redis y fallback
"""

import time
import hashlib
from typing import Optional, Dict, Any, Tuple
from flask import request, g, current_app
from functools import wraps
import logging
from app.config.redis_config import get_redis_client, is_redis_available

logger = logging.getLogger(__name__)

class RateLimitExceeded(Exception):
    """Excepción cuando se excede el límite de velocidad"""
    
    def __init__(self, message: str, retry_after: int):
        super().__init__(message)
        self.retry_after = retry_after

class RateLimiterEnhanced:
    """Rate limiter profesional con Redis y fallback en memoria"""
    
    def __init__(self):
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        self._cleanup_interval = 300  # 5 minutos
        self._last_cleanup = time.time()
    
    def _get_client_identifier(self) -> str:
        """Obtener identificador único del cliente"""
        # Priorizar IP real si está disponible (detrás de proxy)
        ip = request.headers.get('X-Forwarded-For', request.headers.get('X-Real-IP', request.remote_addr))
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        
        # Combinar IP con User-Agent para mayor precisión
        user_agent = request.headers.get('User-Agent', '')
        identifier = f"{ip}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
        
        return identifier
    
    def _get_key(self, identifier: str, endpoint: str, method: str) -> str:
        """Generar clave única para el rate limiting"""
        return f"rate_limit:{endpoint}:{method}:{identifier}"
    
    def _cleanup_memory_store(self):
        """Limpiar store en memoria de entradas expiradas"""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        expired_keys = []
        for key, data in self._memory_store.items():
            if current_time > data['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._memory_store[key]
        
        self._last_cleanup = current_time
        logger.debug(f"Cleaned up {len(expired_keys)} expired rate limit entries")
    
    def _check_rate_limit_redis(self, key: str, limit: int, window: int) -> Tuple[bool, Dict[str, Any]]:
        """Verificar rate limit usando Redis"""
        try:
            redis_client = get_redis_client()
            if not redis_client:
                return False, {}
            
            current_time = int(time.time())
            window_start = current_time - window
            
            # Usar pipeline para operaciones atómicas
            pipe = redis_client.pipeline()
            
            # Remover entradas expiradas
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Contar requests en la ventana
            pipe.zcard(key)
            
            # Agregar request actual
            pipe.zadd(key, {str(current_time): current_time})
            
            # Establecer expiración
            pipe.expire(key, window)
            
            results = pipe.execute()
            current_count = results[1]
            
            # Verificar límite
            if current_count >= limit:
                # Obtener tiempo del request más antiguo
                oldest_requests = redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_requests:
                    oldest_time = int(oldest_requests[0][1])
                    retry_after = window - (current_time - oldest_time)
                else:
                    retry_after = window
                
                return False, {
                    'limit': limit,
                    'remaining': 0,
                    'reset_time': current_time + retry_after,
                    'retry_after': retry_after
                }
            
            return True, {
                'limit': limit,
                'remaining': limit - current_count - 1,
                'reset_time': current_time + window,
                'retry_after': 0
            }
            
        except Exception as e:
            logger.warning(f"Redis rate limit check failed: {e}")
            return False, {}
    
    def _check_rate_limit_memory(self, key: str, limit: int, window: int) -> Tuple[bool, Dict[str, Any]]:
        """Verificar rate limit usando memoria local"""
        current_time = time.time()
        
        # Limpiar entradas expiradas
        self._cleanup_memory_store()
        
        # Obtener o crear entrada
        if key not in self._memory_store:
            self._memory_store[key] = {
                'requests': [],
                'expires_at': current_time + window
            }
        
        entry = self._memory_store[key]
        
        # Remover requests expirados
        window_start = current_time - window
        entry['requests'] = [req_time for req_time in entry['requests'] if req_time > window_start]
        
        # Verificar límite
        if len(entry['requests']) >= limit:
            # Calcular tiempo de retry
            oldest_request = min(entry['requests']) if entry['requests'] else current_time
            retry_after = int(window - (current_time - oldest_request))
            
            return False, {
                'limit': limit,
                'remaining': 0,
                'reset_time': current_time + retry_after,
                'retry_after': retry_after
            }
        
        # Agregar request actual
        entry['requests'].append(current_time)
        
        return True, {
            'limit': limit,
            'remaining': limit - len(entry['requests']),
            'reset_time': current_time + window,
            'retry_after': 0
        }
    
    def check_rate_limit(self, limit: int, window: int, endpoint: str = None, method: str = None) -> Tuple[bool, Dict[str, Any]]:
        """Verificar rate limit con fallback automático"""
        identifier = self._get_client_identifier()
        endpoint = endpoint or request.endpoint or request.path
        method = method or request.method
        
        key = self._get_key(identifier, endpoint, method)
        
        # Intentar Redis primero
        if is_redis_available():
            success, info = self._check_rate_limit_redis(key, limit, window)
            if success is not False:  # No es False (puede ser True o None)
                return success, info
        
        # Fallback a memoria
        return self._check_rate_limit_memory(key, limit, window)
    
    def get_rate_limit_info(self, endpoint: str = None, method: str = None) -> Dict[str, Any]:
        """Obtener información de rate limit sin aplicar límite"""
        identifier = self._get_client_identifier()
        endpoint = endpoint or request.endpoint or request.path
        method = method or request.method
        
        key = self._get_key(identifier, endpoint, method)
        
        # Intentar Redis primero
        if is_redis_available():
            try:
                redis_client = get_redis_client()
                if redis_client:
                    current_time = int(time.time())
                    count = redis_client.zcard(key)
                    ttl = redis_client.ttl(key)
                    
                    return {
                        'current_requests': count,
                        'ttl': ttl,
                        'storage': 'redis'
                    }
            except Exception as e:
                logger.warning(f"Redis rate limit info failed: {e}")
        
        # Fallback a memoria
        if key in self._memory_store:
            entry = self._memory_store[key]
            current_time = time.time()
            window_start = current_time - 3600  # 1 hora por defecto
            valid_requests = [req_time for req_time in entry['requests'] if req_time > window_start]
            
            return {
                'current_requests': len(valid_requests),
                'ttl': int(entry['expires_at'] - current_time) if entry['expires_at'] > current_time else 0,
                'storage': 'memory'
            }
        
        return {
            'current_requests': 0,
            'ttl': 0,
            'storage': 'memory'
        }

# Instancia global del rate limiter
rate_limiter = RateLimiterEnhanced()

def rate_limit(limit: int, window: int = 60, per: str = 'endpoint'):
    """
    Decorator para rate limiting
    
    Args:
        limit: Número máximo de requests
        window: Ventana de tiempo en segundos
        per: 'endpoint', 'ip', o 'user'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Verificar rate limit
                allowed, info = rate_limiter.check_rate_limit(limit, window)
                
                if not allowed:
                    # Agregar headers de rate limit
                    response = current_app.response_class(
                        response='{"error": "Rate limit exceeded"}',
                        status=429,
                        mimetype='application/json'
                    )
                    
                    response.headers['X-RateLimit-Limit'] = str(info['limit'])
                    response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
                    response.headers['X-RateLimit-Reset'] = str(info['reset_time'])
                    response.headers['Retry-After'] = str(info['retry_after'])
                    
                    logger.warning(f"Rate limit exceeded for {request.remote_addr}: {info}")
                    return response
                
                # Agregar headers de rate limit a la respuesta
                response = f(*args, **kwargs)
                
                if hasattr(response, 'headers'):
                    response.headers['X-RateLimit-Limit'] = str(info['limit'])
                    response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
                    response.headers['X-RateLimit-Reset'] = str(info['reset_time'])
                
                return response
                
            except Exception as e:
                logger.error(f"Rate limit check failed: {e}")
                # En caso de error, permitir el request
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Configuraciones predefinidas
RATE_LIMITS = {
    'strict': {'limit': 10, 'window': 60},      # 10 requests por minuto
    'moderate': {'limit': 100, 'window': 60},   # 100 requests por minuto
    'lenient': {'limit': 1000, 'window': 60},   # 1000 requests por minuto
    'api': {'limit': 200, 'window': 60},        # 200 requests por minuto para API
    'auth': {'limit': 5, 'window': 300},        # 5 intentos de login por 5 minutos
    'upload': {'limit': 10, 'window': 3600},    # 10 uploads por hora
}

def apply_rate_limit(limit_type: str = 'moderate'):
    """Aplicar rate limit predefinido"""
    config = RATE_LIMITS.get(limit_type, RATE_LIMITS['moderate'])
    return rate_limit(config['limit'], config['window'])
