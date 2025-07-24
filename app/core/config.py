import os
from datetime import timedelta

class Config:
    # Configuración básica
    SECRET_KEY = os.getenv('SECRET_KEY', 'mi_clave_secreta_desarrollo')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Base de datos
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, '..', '..', 'instance', 'app.db'))
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secreto-desarrollo')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Configuración de la aplicación
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    TESTING = False
    
    # Límites y umbrales
    LOW_STOCK_THRESHOLD = int(os.getenv('LOW_STOCK_THRESHOLD', '5'))
    MAX_SEARCH_RESULTS = 50
    RATE_LIMIT = "100/minute"
    
    # CORS
    CORS_HEADERS = 'Content-Type'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    
    # En producción, asegurarse de que las claves secretas estén configuradas
    def __init__(self):
        if 'SECRET_KEY' not in os.environ:
            raise ValueError("No SECRET_KEY set for Production environment")
        if 'JWT_SECRET_KEY' not in os.environ:
            raise ValueError("No JWT_SECRET_KEY set for Production environment")

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}