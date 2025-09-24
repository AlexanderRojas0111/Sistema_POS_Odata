import os
from datetime import timedelta

class Config:
    """Configuración base"""
    
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,
        'max_overflow': 30,
        'pool_timeout': 30,
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # CORS Configuration - Más restrictivo por defecto
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_EXPOSE_HEADERS = ['Content-Type', 'Authorization']
    
    # Rate Limiting - DESHABILITADO TEMPORALMENTE PARA HEALTH CHECK
    RATELIMIT_ENABLED = False
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    RATELIMIT_DEFAULT = "200 per day;50 per hour;10 per minute"
    RATELIMIT_STRATEGY = "fixed-window"
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # File Upload - Límites más estrictos
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB máximo
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # Pagination
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100
    
    # Cache
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'pos_odata_'
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    }

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    
    DEBUG = True
    TESTING = False
    ENV = 'development'
    
    # Base de datos local (SQLite para desarrollo rápido)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///pos_odata_dev.db'
    
    # Configuración específica para SQLite en desarrollo
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Logging detallado
    LOG_LEVEL = 'DEBUG'
    
    # CORS permisivo para desarrollo pero más seguro
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5000']
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Security relajado para desarrollo pero no completamente
    SESSION_COOKIE_SECURE = False  # HTTP en desarrollo
    SESSION_COOKIE_SAMESITE = 'Lax'  # Más permisivo en desarrollo
    
    # Auto-reload
    TEMPLATES_AUTO_RELOAD = True
    
    # Rate limiting más permisivo en desarrollo
    RATELIMIT_DEFAULT = "1000 per day;200 per hour;50 per minute"
    
    # Deshabilitar Rate limiting en desarrollo para evitar problemas con Redis
    RATELIMIT_ENABLED = False

class TestingConfig(Config):
    """Configuración para testing"""
    
    TESTING = True
    DEBUG = False
    ENV = 'testing'
    
    # Base de datos en memoria para tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Configuración específica para SQLite
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Deshabilitar CSRF para tests
    WTF_CSRF_ENABLED = False
    
    # Logging mínimo para tests
    LOG_LEVEL = 'ERROR'
    
    # Cache deshabilitado para tests
    CACHE_TYPE = 'null'
    
    # Redis deshabilitado para tests
    REDIS_URL = 'redis://localhost:6379/0'  # Se usará MockRedis automáticamente
    
    # Rate limiting deshabilitado para tests
    RATELIMIT_ENABLED = False

class StagingConfig(Config):
    """Configuración para staging"""
    
    DEBUG = False
    TESTING = False
    ENV = 'staging'
    
    # Base de datos de staging
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@staging-db:5432/pos_odata_staging'
    
    # Security intermedio
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # CORS para staging
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://staging.pos-odata.com').split(',')
    
    # Logging para staging
    LOG_LEVEL = 'INFO'
    
    # Rate limiting activo
    RATELIMIT_ENABLED = True
    
    # Cache activo
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 600

class ProductionConfig(Config):
    """Configuración para producción"""
    
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Base de datos de producción
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Security máximo
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # CORS restringido para producción
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://pos-odata.com').split(',')
    
    # Logging para producción
    LOG_LEVEL = 'WARNING'
    
    # Rate limiting estricto
    RATELIMIT_ENABLED = True
    
    # Cache agresivo
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 3600
    
    # Configuración de pool de conexiones
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 20,
        'max_overflow': 30,
    }

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}