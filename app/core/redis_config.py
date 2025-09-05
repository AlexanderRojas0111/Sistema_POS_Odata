#!/usr/bin/env python3
"""
Configuración de Redis - O'Data v2.0.0
======================================

Configuración para:
- Cache de aplicaciones
- Rate limiting
- Sesiones
- Colas de tareas

Autor: Sistema POS Odata
Versión: 2.0.0
"""

import os
import logging
from typing import Optional, Dict, Any
from redis import Redis, ConnectionPool, RedisError
from redis.exceptions import ConnectionError, TimeoutError
import json
import pickle
from functools import wraps
from flask import request, jsonify, current_app
import time

logger = logging.getLogger(__name__)

class RedisManager:
    """Gestor de conexiones y operaciones Redis"""
    
    def __init__(self, app=None):
        self.app = app
        self.redis_client: Optional[Redis] = None
        self.connection_pool: Optional[ConnectionPool] = None
        self.is_connected = False
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar Redis con la aplicación Flask"""
        self.app = app
        
        # Configuración de Redis
        redis_config = {
            'host': app.config.get('REDIS_HOST', 'localhost'),
            'port': app.config.get('REDIS_PORT', 6379),
            'db': app.config.get('REDIS_DB', 0),
            'password': app.config.get('REDIS_PASSWORD'),
            'decode_responses': False,  # Para cache de objetos
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'retry_on_timeout': True,
            'health_check_interval': 30
        }
        
        try:
            # Crear pool de conexiones
            self.connection_pool = ConnectionPool(**redis_config)
            self.redis_client = Redis(connection_pool=self.connection_pool)
            
            # Verificar conexión
            self.redis_client.ping()
            self.is_connected = True
            
            logger.info(f"Redis conectado exitosamente en {redis_config['host']}:{redis_config['port']}")
            
        except (ConnectionError, TimeoutError, RedisError) as e:
            logger.warning(f"Redis no disponible: {e}. Usando modo sin cache.")
            self.is_connected = False
            self.redis_client = None
    
    def get_client(self) -> Optional[Redis]:
        """Obtener cliente Redis activo"""
        if not self.is_connected or not self.redis_client:
            return None
        
        try:
            # Verificar conexión
            self.redis_client.ping()
            return self.redis_client
        except (ConnectionError, TimeoutError, RedisError):
            logger.warning("Conexión Redis perdida, reintentando...")
            self.is_connected = False
            return None
    
    def set_cache(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Establecer valor en cache"""
        client = self.get_client()
        if not client:
            return False
        
        try:
            # Serializar valor
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value, default=str)
            else:
                serialized = pickle.dumps(value)
            
            client.setex(key, expire, serialized)
            return True
        except Exception as e:
            logger.error(f"Error estableciendo cache: {e}")
            return False
    
    def get_cache(self, key: str, default: Any = None) -> Any:
        """Obtener valor del cache"""
        client = self.get_client()
        if not client:
            return default
        
        try:
            value = client.get(key)
            if value is None:
                return default
            
            # Intentar deserializar JSON primero
            try:
                return json.loads(value)
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Si falla JSON, usar pickle
                return pickle.loads(value)
                
        except Exception as e:
            logger.error(f"Error obteniendo cache: {e}")
            return default
    
    def delete_cache(self, key: str) -> bool:
        """Eliminar clave del cache"""
        client = self.get_client()
        if not client:
            return False
        
        try:
            return bool(client.delete(key))
        except Exception as e:
            logger.error(f"Error eliminando cache: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Eliminar claves por patrón"""
        client = self.get_client()
        if not client:
            return 0
        
        try:
            keys = client.keys(pattern)
            if keys:
                return client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error eliminando patrón {pattern}: {e}")
            return 0
    
    def increment_counter(self, key: str, expire: int = 3600) -> int:
        """Incrementar contador para rate limiting"""
        client = self.get_client()
        if not client:
            return 0
        
        try:
            pipe = client.pipeline()
            pipe.incr(key)
            pipe.expire(key, expire)
            result = pipe.execute()
            return result[0]
        except Exception as e:
            logger.error(f"Error incrementando contador: {e}")
            return 0
    
    def get_counter(self, key: str) -> int:
        """Obtener valor del contador"""
        client = self.get_client()
        if not client:
            return 0
        
        try:
            value = client.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"Error obteniendo contador: {e}")
            return 0

# Instancia global
redis_manager = RedisManager()

def cache_response(timeout: int = 300, key_prefix: str = "cache"):
    """Decorador para cache de respuestas"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not redis_manager.is_connected:
                return f(*args, **kwargs)
            
            # Generar clave única
            cache_key = f"{key_prefix}:{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Intentar obtener del cache
            cached_result = redis_manager.get_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función
            result = f(*args, **kwargs)
            
            # Guardar en cache
            redis_manager.set_cache(cache_key, result, timeout)
            
            return result
        return decorated_function
    return decorator

def rate_limit(requests: int = 100, window: int = 3600, key_prefix: str = "rate_limit"):
    """Decorador para rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not redis_manager.is_connected:
                return f(*args, **kwargs)
            
            # Generar clave única por IP
            client_ip = request.remote_addr
            rate_key = f"{key_prefix}:{client_ip}:{f.__name__}"
            
            # Verificar límite
            current_count = redis_manager.get_counter(rate_key)
            if current_count >= requests:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Máximo {requests} requests por {window} segundos',
                    'retry_after': window
                }), 429
            
            # Incrementar contador
            redis_manager.increment_counter(rate_key, window)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Funciones de utilidad para cache
def invalidate_product_cache(product_id: int = None):
    """Invalidar cache de productos"""
    if product_id:
        redis_manager.delete_cache(f"cache:get_product:{product_id}")
    redis_manager.clear_pattern("cache:get_products*")
    redis_manager.clear_pattern("cache:search_products*")

def invalidate_sales_cache(sale_id: int = None):
    """Invalidar cache de ventas"""
    if sale_id:
        redis_manager.delete_cache(f"cache:get_sale:{sale_id}")
    redis_manager.clear_pattern("cache:get_sales*")
    redis_manager.clear_pattern("cache:search_sales*")
    redis_manager.clear_pattern("cache:reports*")

def invalidate_user_cache(user_id: int = None):
    """Invalidar cache de usuarios"""
    if user_id:
        redis_manager.delete_cache(f"cache:get_user:{user_id}")
    redis_manager.clear_pattern("cache:get_users*")
    redis_manager.clear_pattern("cache:search_users*")
