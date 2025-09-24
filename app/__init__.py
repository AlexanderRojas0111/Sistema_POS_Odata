"""
Sistema POS O'data - Aplicación Flask Principal
===============================================

Sistema de Punto de Venta con funcionalidades avanzadas de IA
para búsqueda semántica y recomendaciones inteligentes.

Autor: Sistema POS Odata
Versión: 2.0.0
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
import redis
import logging
import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional

# Imports condicionales para flask-limiter
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    FLASK_LIMITER_AVAILABLE = True
except ImportError:
    FLASK_LIMITER_AVAILABLE = False
    Limiter = None
    get_remote_address = None

from app.core.database import db, init_db
from app.core.config import config
from app.core.exceptions import register_error_handlers
from app.core.logging_config import setup_logging, setup_request_logging
from app.core.metrics import setup_metrics, register_metrics_endpoints

# Constantes de la aplicación
APP_VERSION = "2.0.0"
API_TITLE = "POS O'data API"

def create_app(config_name=None):
    """Crea y configura la aplicación Flask"""
    
    # Crear la aplicación Flask
    app = Flask(__name__, instance_relative_config=True)
    
    # Asegurar que existe el directorio instance
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Configurar la aplicación
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Configurar logging empresarial
    setup_logging(app)
    setup_request_logging(app)
    
    # Inicializar extensiones
    CORS(app, 
          origins=app.config['CORS_ORIGINS'],
          supports_credentials=app.config['CORS_SUPPORTS_CREDENTIALS'],
          expose_headers=app.config['CORS_EXPOSE_HEADERS'])
    
    init_db(app)
    Migrate(app, db)
    JWTManager(app)
    
    # Configurar Rate Limiting solo si está disponible y habilitado
    rate_limiting_enabled = app.config.get('RATELIMIT_ENABLED', False)
    
    if FLASK_LIMITER_AVAILABLE and rate_limiting_enabled:
        try:
            # Usar MockRedis si el Redis real no está disponible
            storage_uri = None
            if hasattr(app, 'redis') and hasattr(app.redis, '_data'):
                # Es MockRedis, no usar storage_uri
                app.logger.info('Usando MockRedis - Rate limiting básico deshabilitado')
                app.limiter = None
            else:
                # Redis real disponible
                storage_uri = app.config.get('RATELIMIT_STORAGE_URL', app.config.get('REDIS_URL'))
                limiter = Limiter(
                    app=app,
                    key_func=get_remote_address,
                    default_limits=app.config.get('RATELIMIT_DEFAULT', '200 per day;50 per hour;10 per minute').split(';'),
                    storage_uri=storage_uri,
                    strategy=app.config.get('RATELIMIT_STRATEGY', 'fixed-window')
                )
                app.limiter = limiter
                app.logger.info('Rate limiting configurado correctamente')
        except Exception as e:
            app.logger.warning(f'No se pudo configurar rate limiting: {e}')
            app.limiter = None
    else:
        app.limiter = None
        if not FLASK_LIMITER_AVAILABLE:
            app.logger.warning('Flask-Limiter no está disponible. Rate limiting deshabilitado.')
        elif not rate_limiting_enabled:
            app.logger.info('Rate limiting deshabilitado por configuración')
        else:
            app.logger.info('Rate limiting deshabilitado')
    
    # Configurar Redis con manejo de errores
    try:
        app.redis = redis.from_url(app.config['REDIS_URL'])
        # Probar conexión
        app.redis.ping()
        app.logger.info('Redis conectado correctamente')
    except Exception as e:
        app.logger.warning(f'Redis no disponible: {e}. Usando modo sin cache.')
        # Crear un mock de Redis para desarrollo
        class MockRedis:
            def __init__(self):
                self._data = {}
            
            def ping(self): return True
            def get(self, key): return self._data.get(key)
            def set(self, key, value, ex=None): 
                self._data[key] = value
                return True
            def setex(self, key, time, value):
                self._data[key] = value
                return True
            def incr(self, key):
                current = int(self._data.get(key, 0))
                self._data[key] = str(current + 1)
                return current + 1
            def delete(self, *keys): 
                for key in keys:
                    self._data.pop(key, None)
                return len(keys)
            def exists(self, key): return key in self._data
            def flushdb(self): 
                self._data.clear()
                return True
            def keys(self, pattern): 
                # Implementación simple de pattern matching
                import fnmatch
                return [k for k in self._data.keys() if fnmatch.fnmatch(k, pattern.replace('*', '*'))]
        app.redis = MockRedis()
    
    # Inicializar Cache Manager
    from app.core.cache import init_cache
    init_cache(app)
    
    # Inicializar Security Manager con manejo de errores
    try:
        from app.core.security import init_security
        init_security(app)
    except Exception as e:
        app.logger.warning(f'Error inicializando SecurityManager: {e}. Continuando sin funciones avanzadas de seguridad.')
    
    # Registrar blueprints
    from app.api.v1.routes import api_v1
    from app.api.v2.routes import api_v2
    
    app.register_blueprint(api_v1, url_prefix='/api/v1')
    app.register_blueprint(api_v2, url_prefix='/api/v2')
    
    # Registrar endpoints básicos
    register_basic_routes(app)

    # Eximir endpoints de health del rate limiting (si está habilitado)
    try:
        if getattr(app, 'limiter', None):
            # Endpoint básico '/health'
            if 'health_check' in app.view_functions:
                app.limiter.exempt(app.view_functions['health_check'])
            # Endpoint de IA '/ai/health' a través del blueprint 'ai'
            if 'ai.ai_health' in app.view_functions:
                app.limiter.exempt(app.view_functions['ai.ai_health'])
    except Exception as e:
        app.logger.warning(f'No se pudieron eximir endpoints de health del rate limiting: {e}')
    
    # Registrar manejadores de errores empresariales
    register_error_handlers(app)
    
    # Configurar sistema de métricas y monitoreo
    setup_metrics(app)
    register_metrics_endpoints(app)
    
    # Configurar headers de seguridad
    setup_security_headers(app)
    
    app.logger.info(f"Aplicación POS O'Data v{APP_VERSION} iniciada exitosamente")
    
    return app

def register_basic_routes(app):
    """Registra las rutas básicas de la aplicación"""
    
    @app.route('/health')
    def health_check():
        """Endpoint de health check para monitoreo"""
        return {
            'status': 'healthy',
            'version': '1.0.0',
            'environment': app.config.get('ENV', 'development'),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
    
    @app.route('/ai-test')
    def ai_test():
        """Endpoint de prueba para IA"""
        return {
            'status': 'AI endpoints working',
            'version': '2.0.0',
            'message': 'Los endpoints de IA están funcionando correctamente',
            'features': [
                'Búsqueda semántica',
                'Recomendaciones inteligentes',
                'Análisis de texto'
            ]
        }
    
    @app.route('/')
    def index():
        """Endpoint raíz de la aplicación"""
        return {
            'message': 'POS O\'data API',
            'version': '1.0.0',
            'docs': '/api/v1/docs' if app.config.get('ENV') == 'development' else None
        }

def register_error_handlers(app):
    """Registra los manejadores de errores de la aplicación"""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return {'error': 'Bad Request', 'message': str(error)}, 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return {'error': 'Unauthorized', 'message': 'Authentication required'}, 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return {'error': 'Forbidden', 'message': 'Insufficient permissions'}, 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not Found', 'message': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return {'error': 'Internal Server Error', 'message': 'An internal error occurred'}, 500

def setup_security_headers(app):
    """Configura headers de seguridad en todas las respuestas"""
    
    @app.after_request
    def add_security_headers(response):
        for header, value in app.config['SECURITY_HEADERS'].items():
            response.headers[header] = value
        return response
