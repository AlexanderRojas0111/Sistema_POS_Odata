import json
import time
import hashlib
from typing import Any, Optional, Dict, List
from functools import wraps
import redis
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Gestor de caché optimizado para el sistema POS"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_ttl = 300  # 5 minutos por defecto
        
        # Configuración de caché por tipo de dato
        self.cache_config = {
            'products': {
                'ttl': 600,  # 10 minutos
                'max_size': 1000,
                'compression': True
            },
            'sales': {
                'ttl': 300,  # 5 minutos
                'max_size': 500,
                'compression': False
            },
            'inventory': {
                'ttl': 180,  # 3 minutos
                'max_size': 200,
                'compression': True
            },
            'search_results': {
                'ttl': 120,  # 2 minutos
                'max_size': 100,
                'compression': True
            },
            'user_sessions': {
                'ttl': 3600,  # 1 hora
                'max_size': 100,
                'compression': False
            },
            'reports': {
                'ttl': 1800,  # 30 minutos
                'max_size': 50,
                'compression': True
            }
        }
    
    def generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Genera clave de caché única"""
        # Crear string con todos los argumentos
        key_parts = [prefix]
        
        # Agregar argumentos posicionales
        for arg in args:
            key_parts.append(str(arg))
        
        # Agregar argumentos nombrados ordenados
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        # Crear hash de la clave
        key_string = ":".join(key_parts)
        return f"cache:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene valor del caché"""
        try:
            value = self.redis.get(key)
            if value is None:
                return default
            
            # Intentar deserializar JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # Si no es JSON, devolver como string
                return value.decode('utf-8')
                
        except Exception as e:
            logger.error(f"Error obteniendo caché {key}: {e}")
            return default
    
    def set(self, key: str, value: Any, ttl: int = None, cache_type: str = None) -> bool:
        """Establece valor en caché"""
        try:
            # Determinar TTL
            if ttl is None and cache_type:
                ttl = self.cache_config.get(cache_type, {}).get('ttl', self.default_ttl)
            elif ttl is None:
                ttl = self.default_ttl
            
            # Serializar valor
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False)
            else:
                serialized_value = str(value)
            
            # Comprimir si está configurado
            if cache_type and self.cache_config.get(cache_type, {}).get('compression', False):
                import gzip
                serialized_value = gzip.compress(serialized_value.encode('utf-8'))
            
            # Guardar en Redis
            if ttl > 0:
                return self.redis.setex(key, ttl, serialized_value)
            else:
                return self.redis.set(key, serialized_value)
                
        except Exception as e:
            logger.error(f"Error estableciendo caché {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Elimina clave del caché"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.error(f"Error eliminando caché {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Verifica si existe una clave"""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"Error verificando caché {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Establece tiempo de expiración"""
        try:
            return bool(self.redis.expire(key, ttl))
        except Exception as e:
            logger.error(f"Error estableciendo expiración {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Elimina todas las claves que coincidan con un patrón"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error limpiando caché con patrón {pattern}: {e}")
            return 0
    
    def get_or_set(self, key: str, callback: callable, ttl: int = None, cache_type: str = None) -> Any:
        """Obtiene valor del caché o lo establece si no existe"""
        # Intentar obtener del caché
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Si no existe, ejecutar callback
        try:
            value = callback()
            self.set(key, value, ttl, cache_type)
            return value
        except Exception as e:
            logger.error(f"Error en get_or_set para {key}: {e}")
            return None
    
    def invalidate_related(self, pattern: str):
        """Invalida caché relacionado con un patrón"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
                logger.info(f"Invalidados {len(keys)} elementos de caché con patrón: {pattern}")
        except Exception as e:
            logger.error(f"Error invalidando caché con patrón {pattern}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché"""
        try:
            info = self.redis.info()
            return {
                'total_keys': info.get('db0', {}).get('keys', 0),
                'memory_usage': info.get('used_memory_human', 'N/A'),
                'hit_rate': self.calculate_hit_rate(),
                'cache_size': self.get_cache_size()
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de caché: {e}")
            return {}
    
    def calculate_hit_rate(self) -> float:
        """Calcula tasa de aciertos del caché"""
        try:
            # Implementar cálculo de hit rate basado en métricas de Redis
            # Esto es una implementación simplificada
            return 0.85  # Placeholder
        except Exception as e:
            logger.error(f"Error calculando hit rate: {e}")
            return 0.0
    
    def get_cache_size(self) -> Dict[str, int]:
        """Obtiene tamaño del caché por tipo"""
        try:
            sizes = {}
            for cache_type in self.cache_config.keys():
                pattern = f"cache:*{cache_type}*"
                keys = self.redis.keys(pattern)
                sizes[cache_type] = len(keys)
            return sizes
        except Exception as e:
            logger.error(f"Error obteniendo tamaño de caché: {e}")
            return {}
    
    def optimize_cache(self):
        """Optimiza el caché eliminando elementos antiguos"""
        try:
            for cache_type, config in self.cache_config.items():
                pattern = f"cache:*{cache_type}*"
                keys = self.redis.keys(pattern)
                
                if len(keys) > config.get('max_size', 100):
                    # Eliminar elementos más antiguos
                    keys_to_delete = keys[config['max_size']:]
                    if keys_to_delete:
                        self.redis.delete(*keys_to_delete)
                        logger.info(f"Optimizado caché {cache_type}: eliminados {len(keys_to_delete)} elementos")
                        
        except Exception as e:
            logger.error(f"Error optimizando caché: {e}")

# Decoradores de caché
def cached(ttl: int = None, cache_type: str = None, key_prefix: str = None):
    """Decorador para caché automático"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = getattr(wrapper, '_cache_manager', None)
            if cache_manager is None:
                return func(*args, **kwargs)
            
            # Generar clave de caché
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = cache_manager.generate_cache_key(prefix, *args, **kwargs)
            
            # Intentar obtener del caché
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y guardar resultado
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl, cache_type)
            
            return result
        return wrapper
    return decorator

def cache_invalidate(pattern: str):
    """Decorador para invalidar caché después de ejecutar función"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidar caché relacionado
            cache_manager = getattr(wrapper, '_cache_manager', None)
            if cache_manager:
                cache_manager.invalidate_related(pattern)
            
            return result
        return wrapper
    return decorator

def cache_clear():
    """Decorador para limpiar caché después de ejecutar función"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Limpiar todo el caché
            cache_manager = getattr(wrapper, '_cache_manager', None)
            if cache_manager:
                cache_manager.clear_pattern("cache:*")
            
            return result
        return wrapper
    return decorator

# Clase para caché específico de productos
class ProductCache:
    """Caché especializado para productos"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.prefix = "products"
    
    def get_product(self, product_id: int) -> Optional[Dict]:
        """Obtiene producto del caché"""
        key = f"cache:{self.prefix}:{product_id}"
        return self.cache.get(key)
    
    def set_product(self, product_id: int, product_data: Dict):
        """Establece producto en caché"""
        key = f"cache:{self.prefix}:{product_id}"
        self.cache.set(key, product_data, cache_type='products')
    
    def get_products_list(self, filters: Dict = None) -> Optional[List]:
        """Obtiene lista de productos del caché"""
        key = self.cache.generate_cache_key(f"{self.prefix}:list", **filters or {})
        return self.cache.get(key)
    
    def set_products_list(self, products_data: List, filters: Dict = None):
        """Establece lista de productos en caché"""
        key = self.cache.generate_cache_key(f"{self.prefix}:list", **filters or {})
        self.cache.set(key, products_data, cache_type='products')
    
    def invalidate_product(self, product_id: int):
        """Invalida caché de un producto específico"""
        self.cache.delete(f"cache:{self.prefix}:{product_id}")
        # También invalidar listas que puedan contener este producto
        self.cache.invalidate_related(f"cache:{self.prefix}:list*")
    
    def invalidate_all_products(self):
        """Invalida todo el caché de productos"""
        self.cache.invalidate_related(f"cache:{self.prefix}*")

# Clase para caché específico de búsquedas
class SearchCache:
    """Caché especializado para resultados de búsqueda"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.prefix = "search"
    
    def get_search_results(self, query: str, search_type: str = "semantic") -> Optional[List]:
        """Obtiene resultados de búsqueda del caché"""
        key = self.cache.generate_cache_key(f"{self.prefix}:{search_type}", query=query)
        return self.cache.get(key)
    
    def set_search_results(self, query: str, results: List, search_type: str = "semantic"):
        """Establece resultados de búsqueda en caché"""
        key = self.cache.generate_cache_key(f"{self.prefix}:{search_type}", query=query)
        self.cache.set(key, results, cache_type='search_results')
    
    def invalidate_search_cache(self):
        """Invalida todo el caché de búsquedas"""
        self.cache.invalidate_related(f"cache:{self.prefix}*")

# Instancia global del gestor de caché
cache_manager = None

def init_cache(app):
    """Inicializa el gestor de caché"""
    global cache_manager
    cache_manager = CacheManager(app.redis)
    app.cache_manager = cache_manager
    
    # Crear instancias especializadas
    app.product_cache = ProductCache(cache_manager)
    app.search_cache = SearchCache(cache_manager)
    
    # Configurar decoradores con el gestor de caché
    def configure_cache_decorators():
        for decorator in [cached, cache_invalidate, cache_clear]:
            decorator._cache_manager = cache_manager
    
    configure_cache_decorators() 