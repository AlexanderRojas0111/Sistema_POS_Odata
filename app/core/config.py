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
    }
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # Security
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Cache
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CACHE_DEFAULT_TIMEOUT = 300

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    
    DEBUG = True
    TESTING = False
    ENV = 'development'
    
    # Base de datos local
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/pos_odata_dev'
    
    # Logging detallado
    LOG_LEVEL = 'DEBUG'
    
    # CORS permisivo para desarrollo
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', '*']
    
    # Security relajado para desarrollo
    SESSION_COOKIE_SECURE = False
    
    # Auto-reload
    TEMPLATES_AUTO_RELOAD = True

class TestingConfig(Config):
    """Configuración para testing"""
    
    TESTING = True
    DEBUG = False
    ENV = 'testing'
    
    # Base de datos en memoria para tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Deshabilitar CSRF para tests
    WTF_CSRF_ENABLED = False
    
    # Logging mínimo para tests
    LOG_LEVEL = 'ERROR'
    
    # Cache deshabilitado para tests
    CACHE_TYPE = 'null'

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