#!/usr/bin/env python3
"""
Configuración del Sistema - O'Data v2.0.0
==========================================

Configuración para:
- Entornos de desarrollo y producción
- Base de datos (SQLite/PostgreSQL)
- Redis para cache y rate limiting
- Seguridad y JWT
- Logging y monitoreo

Autor: Sistema POS Odata
Versión: 2.0.0
"""

import os
from datetime import timedelta

class Config:
    """Configuración base"""
    
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Configuración del servidor
    SERVER_HOST = os.environ.get('SERVER_HOST', '127.0.0.1')
    SERVER_PORT = int(os.environ.get('SERVER_PORT', 8000))
    
    # Configuración de base de datos
    DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'sqlite')  # sqlite o postgresql
    
    if DATABASE_TYPE == 'postgresql':
        # PostgreSQL
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            f"postgresql://{os.environ.get('DB_USER', 'odata_user')}:" \
            f"{os.environ.get('DB_PASSWORD', 'odata_password')}@" \
            f"{os.environ.get('DB_HOST', 'localhost')}:" \
            f"{os.environ.get('DB_PORT', '5432')}/" \
            f"{os.environ.get('DB_NAME', 'odata_pos')}"
    else:
        # SQLite (desarrollo)
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///instance/pos_odata_dev.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 10,
        'pool_size': 20
    }
    
    # Configuración de Redis
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    REDIS_USE_CACHE = os.environ.get('REDIS_USE_CACHE', 'True').lower() == 'true'
    REDIS_USE_RATE_LIMIT = os.environ.get('REDIS_USE_RATE_LIMIT', 'True').lower() == 'true'
    
    # Configuración de JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ERROR_MESSAGE_KEY = 'error'
    
    # Configuración de seguridad
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Rate limiting
    RATELIMIT_ENABLED = REDIS_USE_RATE_LIMIT
    RATELIMIT_STORAGE_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_OPTIONS = {
        'socket_connect_timeout': 5,
        'socket_timeout': 5
    }
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    LOG_MAX_SIZE = int(os.environ.get('LOG_MAX_SIZE', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # Configuración de paginación
    DEFAULT_PAGE_SIZE = int(os.environ.get('DEFAULT_PAGE_SIZE', 20))
    MAX_PAGE_SIZE = int(os.environ.get('MAX_PAGE_SIZE', 100))
    
    # Configuración de cache
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))  # 5 minutos
    CACHE_KEY_PREFIX = 'odata_cache'
    
    # Configuración de monitoreo
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'True').lower() == 'true'
    METRICS_PORT = int(os.environ.get('METRICS_PORT', 9090))
    
    # Configuración de auditoría
    AUDIT_LOG_ENABLED = os.environ.get('AUDIT_LOG_ENABLED', 'True').lower() == 'true'
    AUDIT_LOG_FILE = os.environ.get('AUDIT_LOG_FILE', 'logs/audit.log')
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 8 * 1024 * 1024))  # 8MB para seguridad
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    
    # Configuración de sesiones
    SESSION_TYPE = 'redis' if REDIS_USE_CACHE else 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Configuración de compresión
    COMPRESS_MIMETYPES = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript']
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    
    # Headers de seguridad básicos (siempre activos)
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block'
    }

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    DATABASE_TYPE = 'sqlite'
    LOG_LEVEL = 'DEBUG'
    REDIS_USE_CACHE = False  # Deshabilitar en desarrollo si no hay Redis
    REDIS_USE_RATE_LIMIT = False
    
    # Configuraciones de seguridad para desarrollo
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    DATABASE_TYPE = 'postgresql'
    LOG_LEVEL = 'WARNING'
    REDIS_USE_CACHE = True
    REDIS_USE_RATE_LIMIT = True
    
    # Configuraciones de seguridad para producción
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Headers de seguridad adicionales para producción
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    }

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DATABASE_TYPE = 'sqlite'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    REDIS_USE_CACHE = False
    REDIS_USE_RATE_LIMIT = False
    
    # Configuraciones de seguridad para testing
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Headers de seguridad para testing
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block'
    }

# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtener configuración según el entorno"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])

# Instancia global de configuración para importación directa
settings = get_config()