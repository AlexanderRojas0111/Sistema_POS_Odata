from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
import redis
import logging
import datetime
from logging.handlers import RotatingFileHandler

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
    CORS(app)
    init_db(app)
    Migrate(app, db)
    JWTManager(app)
    
    # Configurar Redis
    app.redis = redis.from_url(app.config['REDIS_URL'])
    
    # Registrar blueprints
    from app.api.v1.routes import api_v1
    from app.api.v2.routes import api_v2
    
    app.register_blueprint(api_v1, url_prefix='/api/v1')
    app.register_blueprint(api_v2, url_prefix='/api/v2')
    
    # Registrar endpoints básicos
    register_basic_routes(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
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
