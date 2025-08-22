from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
import redis
import logging
import datetime
from logging.handlers import RotatingFileHandler

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
    
    # Configurar logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Aplicación iniciada')
    
    # Inicializar extensiones
    CORS(app, 
          origins=app.config['CORS_ORIGINS'],
          supports_credentials=app.config['CORS_SUPPORTS_CREDENTIALS'],
          expose_headers=app.config['CORS_EXPOSE_HEADERS'])
    
    init_db(app)
    Migrate(app, db)
    JWTManager(app)
    
    # Configurar Rate Limiting solo si está disponible
    if FLASK_LIMITER_AVAILABLE and app.config.get('RATELIMIT_ENABLED', False):
        try:
            limiter = Limiter(
                app=app,
                key_func=get_remote_address,
                default_limits=app.config.get('RATELIMIT_DEFAULT', '200 per day;50 per hour;10 per minute').split(';'),
                storage_uri=app.config.get('RATELIMIT_STORAGE_URL', app.config.get('REDIS_URL')),
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
        else:
            app.logger.info('Rate limiting deshabilitado por configuración')
    
    # Configurar Redis
    app.redis = redis.from_url(app.config['REDIS_URL'])
    
    # Inicializar Cache Manager
    from app.core.cache import init_cache
    init_cache(app)
    
    # Inicializar Security Manager
    from app.core.security import init_security
    init_security(app)
    
    # Registrar blueprints
    from app.api.v1.routes import api_v1
    from app.api.v2.routes import api_v2
    
    app.register_blueprint(api_v1, url_prefix='/api/v1')
    app.register_blueprint(api_v2, url_prefix='/api/v2')
    
    # Registrar endpoints básicos
    register_basic_routes(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Configurar headers de seguridad
    setup_security_headers(app)
    
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
