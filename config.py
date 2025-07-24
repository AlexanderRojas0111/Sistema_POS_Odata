import os
from datetime import timedelta

class Config:
    # Configuración básica
    SECRET_KEY = os.getenv('SECRET_KEY', 'mi_clave_secreta')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de la base de datos principal
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'instance', 'app.db'))
    
    # Configuración de la base de datos vectorial
    VECTOR_DATABASE_URL = os.getenv('VECTOR_DATABASE_URL', 'postgresql://localhost/vector_db')
    
    # Configuración de Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Configuración de JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Configuración de la aplicación
    LOW_STOCK_THRESHOLD = int(os.getenv('LOW_STOCK_THRESHOLD', '5'))
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Configuración de CORS
    CORS_HEADERS = 'Content-Type'