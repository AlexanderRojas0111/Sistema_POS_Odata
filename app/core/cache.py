import redis
import json
import hashlib
from typing import Any, Optional, Union
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Gestor de cache inteligente con TTL y validación"""
    
    def __init__(self, redis_client: redis.Redis, default_ttl: int = 300):
        self.redis = redis_client
        self.default_ttl = default_ttl
        self.key_prefix = 'pos_odata_'
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Genera una clave única para el cache"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return f"{self.key_prefix}{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Establece un valor en el cache con TTL"""
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            return self.redis.setex(key, ttl, serialized_value)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Elimina una clave del cache"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Elimina todas las claves que coincidan con un patrón"""
        try:
            keys = self.redis.keys(f"{self.key_prefix}{pattern}")
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0
    
    def cache_with_ttl(self, prefix: str, ttl: Optional[int] = None):
        """Decorador para cachear funciones con TTL"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self._generate_key(prefix, *args, **kwargs)
                
                # Intentar obtener del cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {cache_key}")
                    return cached_result
                
                # Ejecutar función y cachear resultado
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                logger.debug(f"Cache miss for {cache_key}, stored result")
                
                return result
            return wrapper
        return decorator

    def invalidate_cache(self, pattern: str) -> int:
        """Invalida cache basado en patrón (útil para actualizaciones)"""
        return self.clear_pattern(pattern)

# Instancia global del cache manager
cache_manager = None

def init_cache(app):
    """Inicializa el cache manager global"""
    global cache_manager
    cache_manager = CacheManager(
        redis_client=app.redis,
        default_ttl=app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
    )
    app.cache_manager = cache_manager
