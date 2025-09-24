"""
Extensiones globales de la aplicación Flask
"""

import redis
import logging
from typing import Optional

# Configurar logger
log = logging.getLogger(__name__)

# Cliente Redis global
redis_client: Optional[redis.Redis] = None

def init_redis_client(redis_url: str = "redis://localhost:6379/0") -> redis.Redis:
    """
    Inicializa el cliente Redis global
    """
    global redis_client
    
    try:
        redis_client = redis.from_url(redis_url)
        # Probar la conexión
        redis_client.ping()
        log.info(f"Redis conectado correctamente en {redis_url}")
        return redis_client
        
    except Exception as e:
        log.warning(f"No se pudo conectar a Redis: {e}. Usando FakeRedis.")
        
        # Usar FakeRedis como fallback
        try:
            import fakeredis
            redis_client = fakeredis.FakeStrictRedis()
            log.info("FakeRedis inicializado como fallback")
            return redis_client
        except ImportError:
            log.error("FakeRedis no está disponible. Rate limiting deshabilitado.")
            redis_client = None
            return None

def get_redis_client() -> Optional[redis.Redis]:
    """
    Obtiene el cliente Redis actual
    """
    return redis_client
