#!/usr/bin/env python3
"""
Configuración de Producción - Sistema POS O'Data
================================================
Configuración específica para ambiente de producción
"""

import os
from datetime import timedelta

class ProductionConfig:
    """Configuración de producción para el sistema POS"""
    
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY', 'production-secret-key-change-this-immediately')
    DEBUG = False
    TESTING = False
    
    # Base de datos
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///pos_production.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Configuración de seguridad
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self';"
    }
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "1000 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_SWALLOW_ERRORS = True
    
    # Rate limits específicos
    RATE_LIMITS = {
        'default': '1000 per hour',
        'login': '5 per minute',
        'api': '1000 per hour',
        'health': '100 per minute'
    }
    
    # Configuración de logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'logs/production.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Configuración de sesiones
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # Configuración de CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost,https://localhost').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_HEADERS = ['Content-Type', 'Authorization', 'X-Requested-With']
    
    # Configuración de cache
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    
    # Configuración de email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@pos-odata.com')
    
    # Configuración de backup
    BACKUP_DIR = os.environ.get('BACKUP_DIR', '/backups')
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', 30))
    BACKUP_MAX_FILES = int(os.environ.get('BACKUP_MAX_FILES', 50))
    
    # Configuración de monitoring
    MONITORING_ENABLED = True
    MONITORING_INTERVAL = int(os.environ.get('MONITORING_INTERVAL', 60))  # segundos
    MONITORING_ALERT_EMAIL = os.environ.get('MONITORING_ALERT_EMAIL')
    
    # Umbrales de alerta
    ALERT_THRESHOLDS = {
        'response_time_ms': 500,
        'error_rate_percent': 2.0,
        'cpu_usage_percent': 80,
        'memory_usage_percent': 85,
        'disk_usage_percent': 90
    }
    
    # Configuración de performance
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(hours=1)
    
    # Configuración de base de datos específica
    DATABASE_CONFIG = {
        'postgresql': {
            'pool_size': 20,
            'max_overflow': 0,
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 20,
            'echo': False
        },
        'sqlite': {
            'pool_size': 1,
            'max_overflow': 0,
            'pool_pre_ping': False,
            'pool_recycle': -1,
            'pool_timeout': 20,
            'echo': False
        }
    }
    
    # Configuración de validación
    VALIDATION_CONFIG = {
        'username_min_length': 3,
        'username_max_length': 50,
        'password_min_length': 8,
        'password_max_length': 128,
        'email_max_length': 255,
        'product_name_max_length': 100,
        'product_description_max_length': 500,
        'sale_notes_max_length': 1000
    }
    
    # Configuración de paginación
    PAGINATION_CONFIG = {
        'default_per_page': 20,
        'max_per_page': 100
    }
    
    # Configuración de timeouts
    TIMEOUTS = {
        'database_query': 30,  # segundos
        'external_api': 10,    # segundos
        'file_upload': 60,     # segundos
        'email_send': 30       # segundos
    }
    
    # Configuración de archivos
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    # Configuración de notificaciones
    NOTIFICATION_CONFIG = {
        'email_enabled': True,
        'sms_enabled': False,
        'push_enabled': False,
        'webhook_enabled': False
    }
    
    # Configuración de auditoría
    AUDIT_CONFIG = {
        'enabled': True,
        'log_all_requests': True,
        'log_sensitive_data': False,
        'retention_days': 90
    }
    
    # Configuración de métricas
    METRICS_CONFIG = {
        'enabled': True,
        'collect_system_metrics': True,
        'collect_business_metrics': True,
        'export_interval': 60  # segundos
    }
    
    # Configuración de desarrollo
    DEVELOPMENT_CONFIG = {
        'auto_reload': False,
        'debug_toolbar': False,
        'profiler': False
    }
    
    # Configuración de testing
    TESTING_CONFIG = {
        'use_test_database': False,
        'mock_external_services': False,
        'generate_test_data': False
    }
    
    @classmethod
    def get_database_config(cls):
        """Obtener configuración específica de base de datos"""
        if cls.DATABASE_URL.startswith('postgresql://'):
            return cls.DATABASE_CONFIG['postgresql']
        else:
            return cls.DATABASE_CONFIG['sqlite']
    
    @classmethod
    def get_rate_limit(cls, endpoint):
        """Obtener rate limit específico para un endpoint"""
        return cls.RATE_LIMITS.get(endpoint, cls.RATE_LIMITS['default'])
    
    @classmethod
    def is_production(cls):
        """Verificar si estamos en producción"""
        return not cls.DEBUG and not cls.TESTING
    
    @classmethod
    def get_security_headers(cls):
        """Obtener headers de seguridad"""
        return cls.SECURITY_HEADERS.copy()
    
    @classmethod
    def validate_config(cls):
        """Validar configuración de producción"""
        errors = []
        
        # Verificar SECRET_KEY
        if cls.SECRET_KEY == 'production-secret-key-change-this-immediately':
            errors.append("SECRET_KEY debe ser cambiada en producción")
        
        # Verificar DATABASE_URL
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL debe estar configurada")
        
        # Verificar directorios
        required_dirs = ['logs', 'data', 'backups']
        for dir_name in required_dirs:
            if not os.path.exists(dir_name):
                errors.append(f"Directorio requerido no existe: {dir_name}")
        
        return errors

# Configuración específica por ambiente
class StagingConfig(ProductionConfig):
    """Configuración de staging (hereda de producción)"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    RATELIMIT_DEFAULT = "2000 per hour"  # Más permisivo para testing

class DevelopmentConfig(ProductionConfig):
    """Configuración de desarrollo"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'
    RATELIMIT_DEFAULT = "10000 per hour"  # Muy permisivo para desarrollo
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-dev-key')
    DATABASE_URL = 'sqlite:///pos_development.db'

# Función para obtener configuración según el ambiente
def get_config(environment='production'):
    """Obtener configuración según el ambiente"""
    configs = {
        'production': ProductionConfig,
        'staging': StagingConfig,
        'development': DevelopmentConfig
    }
    
    config_class = configs.get(environment, ProductionConfig)
    return config_class()

# Validación de configuración al importar
if __name__ == "__main__":
    config = get_config()
    errors = config.validate_config()
    
    if errors:
        print("❌ Errores de configuración encontrados:")
        for error in errors:
            print(f"   • {error}")
        exit(1)
    else:
        print("✅ Configuración válida")
