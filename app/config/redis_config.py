"""
Configuración Redis - Sistema POS O'Data
=======================================
Configuración profesional de Redis para rate limiting y cache
"""

import os
import redis
from redis.sentinel import Sentinel
from redis.exceptions import ConnectionError, TimeoutError
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class RedisConfig:
    """Configuración profesional de Redis"""
    
    def __init__(self):
        self.host = os.environ.get('REDIS_HOST', 'localhost')
        self.port = int(os.environ.get('REDIS_PORT', 6379))
        self.password = os.environ.get('REDIS_PASSWORD')
        self.db = int(os.environ.get('REDIS_DB', 0))
        self.socket_timeout = int(os.environ.get('REDIS_SOCKET_TIMEOUT', 5))
        self.socket_connect_timeout = int(os.environ.get('REDIS_CONNECT_TIMEOUT', 5))
        self.retry_on_timeout = True
        self.max_connections = int(os.environ.get('REDIS_MAX_CONNECTIONS', 20))
        self.health_check_interval = int(os.environ.get('REDIS_HEALTH_CHECK_INTERVAL', 30))
        
        # Configuración de Sentinel (para alta disponibilidad)
        self.sentinel_hosts = os.environ.get('REDIS_SENTINEL_HOSTS', '').split(',')
        self.sentinel_master_name = os.environ.get('REDIS_SENTINEL_MASTER', 'mymaster')
        self.use_sentinel = len(self.sentinel_hosts) > 0 and self.sentinel_hosts[0]
        
        # Configuración de SSL
        self.ssl = os.environ.get('REDIS_SSL', 'false').lower() == 'true'
        self.ssl_cert_reqs = os.environ.get('REDIS_SSL_CERT_REQS', 'required')
        
        self._connection_pool = None
        self._redis_client = None
    
    def create_connection_pool(self) -> redis.ConnectionPool:
        """Crear pool de conexiones Redis"""
        try:
            if self.use_sentinel:
                # Configuración con Sentinel para alta disponibilidad
                sentinel = Sentinel(
                    [(host, self.port) for host in self.sentinel_hosts],
                    socket_timeout=self.socket_timeout,
                    socket_connect_timeout=self.socket_connect_timeout,
                    password=self.password,
                    ssl=self.ssl
                )
                
                master = sentinel.master_for(
                    self.sentinel_master_name,
                    socket_timeout=self.socket_timeout,
                    socket_connect_timeout=self.socket_connect_timeout,
                    password=self.password,
                    db=self.db,
                    ssl=self.ssl
                )
                
                return master.connection_pool
            else:
                # Configuración estándar
                return redis.ConnectionPool(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    db=self.db,
                    socket_timeout=self.socket_timeout,
                    socket_connect_timeout=self.socket_connect_timeout,
                    retry_on_timeout=self.retry_on_timeout,
                    max_connections=self.max_connections,
                    health_check_interval=self.health_check_interval,
                    ssl=self.ssl,
                    ssl_cert_reqs=self.ssl_cert_reqs
                )
        except Exception as e:
            logger.error(f"Error creating Redis connection pool: {e}")
            raise
    
    def get_redis_client(self) -> redis.Redis:
        """Obtener cliente Redis con pool de conexiones"""
        if self._redis_client is None:
            try:
                self._connection_pool = self.create_connection_pool()
                self._redis_client = redis.Redis(
                    connection_pool=self._connection_pool,
                    decode_responses=True
                )
                
                # Verificar conexión
                self._redis_client.ping()
                logger.info("Redis connection established successfully")
                
            except (ConnectionError, TimeoutError) as e:
                logger.error(f"Redis connection failed: {e}")
                # Fallback a configuración en memoria
                self._redis_client = None
                raise
            except Exception as e:
                logger.error(f"Unexpected Redis error: {e}")
                raise
        
        return self._redis_client
    
    def test_connection(self) -> bool:
        """Probar conexión Redis"""
        try:
            client = self.get_redis_client()
            client.ping()
            return True
        except Exception as e:
            logger.warning(f"Redis connection test failed: {e}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Obtener información de conexión"""
        return {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "use_sentinel": self.use_sentinel,
            "sentinel_master": self.sentinel_master_name if self.use_sentinel else None,
            "ssl": self.ssl,
            "max_connections": self.max_connections,
            "health_check_interval": self.health_check_interval
        }

class RedisManager:
    """Gestor profesional de Redis"""
    
    def __init__(self):
        self.config = RedisConfig()
        self._client: Optional[redis.Redis] = None
        self._fallback_mode = False
    
    def get_client(self) -> Optional[redis.Redis]:
        """Obtener cliente Redis con fallback automático"""
        if self._fallback_mode:
            return None
        
        try:
            if self._client is None:
                self._client = self.config.get_redis_client()
            return self._client
        except Exception as e:
            logger.warning(f"Redis unavailable, falling back to in-memory mode: {e}")
            self._fallback_mode = True
            return None
    
    def is_available(self) -> bool:
        """Verificar si Redis está disponible"""
        if self._fallback_mode:
            return False
        
        try:
            client = self.get_client()
            if client:
                client.ping()
                return True
        except Exception:
            pass
        
        return False
    
    def get_info(self) -> Dict[str, Any]:
        """Obtener información del estado de Redis"""
        info = self.config.get_connection_info()
        info.update({
            "available": self.is_available(),
            "fallback_mode": self._fallback_mode
        })
        
        if self.is_available():
            try:
                client = self.get_client()
                if client:
                    redis_info = client.info()
                    info.update({
                        "redis_version": redis_info.get("redis_version"),
                        "used_memory": redis_info.get("used_memory_human"),
                        "connected_clients": redis_info.get("connected_clients"),
                        "uptime": redis_info.get("uptime_in_seconds")
                    })
            except Exception as e:
                logger.warning(f"Could not get Redis info: {e}")
        
        return info

# Instancia global del gestor Redis
redis_manager = RedisManager()

def get_redis_client() -> Optional[redis.Redis]:
    """Función helper para obtener cliente Redis"""
    return redis_manager.get_client()

def is_redis_available() -> bool:
    """Función helper para verificar disponibilidad de Redis"""
    return redis_manager.is_available()

def get_redis_info() -> Dict[str, Any]:
    """Función helper para obtener información de Redis"""
    return redis_manager.get_info()
