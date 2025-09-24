import logging
from functools import wraps
from flask import request
from redis.exceptions import RedisError
import time

# Configurar un logger para este módulo
log = logging.getLogger(__name__)

# Para que esto funcione, asegúrate de tener una instancia de redis_client
# disponible globalmente, por ejemplo, desde un archivo app/extensions.py
try:
    from app.extensions import redis_client
except ImportError:
    import fakeredis
    log.warning("Usando fakeredis. No se pudo importar redis_client desde app.extensions.")
    redis_client = fakeredis.FakeStrictRedis()


class RateLimitExceeded(Exception):
    """Excepción personalizada para cuando se excede el límite de peticiones."""
    pass


def get_client_ip():
    """Obtiene la IP del cliente desde los encabezados de la petición, priorizando X-Forwarded-For."""
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.getlist("X-Forwarded-For")[0]
    return request.remote_addr


def rate_limit(limit: int, per: int, scope_func=get_client_ip):
    """
    Un decorador para limitar la tasa de peticiones de una vista de Flask usando un algoritmo de ventana deslizante en Redis.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Construye una clave única para el cliente y el endpoint
            key = f"rate_limit:{scope_func()}:{func.__name__}"

            try:
                # Usar un pipeline de Redis para ejecutar múltiples comandos de forma atómica y eficiente
                p = redis_client.pipeline()
                
                # 1. Añadir la petición actual con su timestamp como score
                current_time = time.time()
                p.zadd(key, {str(current_time): current_time})
                
                # 2. Eliminar registros antiguos que están fuera de la ventana de tiempo
                p.zremrangebyscore(key, 0, current_time - per)
                
                # 3. Contar el número de peticiones en la ventana actual
                p.zcard(key)
                
                # 4. Asegurar que la clave expire para no dejar datos huérfanos en Redis
                p.expire(key, per)
                
                # Ejecutar todos los comandos en el pipeline
                results = p.execute()
                
                # El resultado de zcard() es el tercer comando en el pipeline (índice 2)
                request_count = results[2]
                
                if request_count > limit:
                    log.warning(f"Límite de peticiones excedido para la clave: {key}")
                    raise RateLimitExceeded
            except RedisError as e:
                # Si Redis falla, es mejor fallar en abierto para no afectar al usuario.
                # Se registra el error para monitoreo.
                log.error(f"Error de Redis en el rate limiter: {e}")
                pass

            return func(*args, **kwargs)
        return wrapper
    return decorator


# Decoradores predefinidos para casos comunes
def rate_limit_10_per_minute(func):
    """Limita a 10 peticiones por minuto"""
    return rate_limit(10, 60)(func)


def rate_limit_5_per_minute(func):
    """Limita a 5 peticiones por minuto"""
    return rate_limit(5, 60)(func)


def rate_limit_100_per_hour(func):
    """Limita a 100 peticiones por hora"""
    return rate_limit(100, 3600)(func)


def rate_limit_1000_per_day(func):
    """Limita a 1000 peticiones por día"""
    return rate_limit(1000, 86400)(func)