#!/usr/bin/env python3
"""
Aplicación Principal - O'Data v2.0.0
====================================

Inicialización de la aplicación Flask con:
- Configuración de base de datos
- Redis para cache y rate limiting
- PostgreSQL para producción
- Extensions y blueprints
- Manejo de errores

Autor: Sistema POS Odata
Versión: 2.0.0
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress

# Importar configuraciones
from app.core.config import get_config
from app.core.redis_config import redis_manager
from app.core.postgresql_config import postgresql_manager

# Importar blueprints
from app.api.v1.routes import api_v1
from app.api.v2.routes import api_v2

# Importar funciones de inicialización
from app.core.database import init_db
from app.core.security import init_security
from app.utils.pagination import setup_pagination, setup_filters, setup_search

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(key_func=get_remote_address)
compress = Compress()

# Configurar logging
def setup_logging(app):
    """Configurar sistema de logging"""
    if not app.debug and not app.testing:
        # Logging para producción
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Log principal de la aplicación
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=app.config['LOG_MAX_SIZE'],
            backupCount=app.config['LOG_BACKUP_COUNT']
        )
        file_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Log de auditoría
        if app.config.get('AUDIT_LOG_ENABLED'):
            audit_handler = RotatingFileHandler(
                app.config['AUDIT_LOG_FILE'],
                maxBytes=app.config['LOG_MAX_SIZE'],
                backupCount=app.config['LOG_BACKUP_COUNT']
            )
            audit_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
            audit_handler.setLevel(logging.INFO)
            
            audit_logger = logging.getLogger('audit')
            audit_logger.addHandler(audit_handler)
            audit_logger.setLevel(logging.INFO)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('O\'Data POS v2.0.0 iniciando...')

def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Configurar logging
    setup_logging(app)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)
    compress.init_app(app)
    
    # Inicializar Redis
    redis_manager.init_app(app)
    
    # Inicializar PostgreSQL si está configurado
    if app.config.get('DATABASE_TYPE') == 'postgresql':
        postgresql_manager.init_app(app)
    
    # Configurar paginación, filtros y búsqueda
    setup_pagination(
        default_page=app.config.get('DEFAULT_PAGE_SIZE', 1),
        default_per_page=app.config.get('DEFAULT_PAGE_SIZE', 20),
        max_per_page=app.config.get('MAX_PAGE_SIZE', 100)
    )
    
    # Configurar filtros por defecto
    default_filters = {
        'name': 'like',
        'category': 'exact',
        'price': 'range',
        'status': 'exact',
        'is_active': 'boolean'
    }
    setup_filters(default_filters)
    
    # Configurar campos de búsqueda por defecto
    default_search_fields = ['name', 'description', 'category']
    setup_search(default_search_fields)
    
    # Inicializar base de datos
    with app.app_context():
        init_db(app)
        init_security(app)
    
    # Registrar blueprints
    app.register_blueprint(api_v1, url_prefix='/api/v1')
    app.register_blueprint(api_v2, url_prefix='/api/v2')
    
    # Ruta principal
    @app.route('/')
    def index():
        return jsonify({
            'message': 'O\'Data POS v2.0.0 API',
            'version': '2.0.0',
            'status': 'running',
            'endpoints': {
                'v1': '/api/v1',
                'v2': '/api/v2',
                'health': '/health',
                'docs': '/docs'
            }
        })
    
    # Ruta de salud
    @app.route('/health')
    def health():
        health_status = {
            'status': 'healthy',
            'version': '2.0.0',
            'database': 'connected' if db.engine else 'disconnected',
            'redis': 'connected' if redis_manager.is_connected else 'disconnected',
            'postgresql': 'connected' if postgresql_manager.is_connected else 'disconnected'
        }
        
        # Verificar estado de la base de datos
        try:
            db.session.execute('SELECT 1')
            health_status['database'] = 'connected'
        except Exception as e:
            health_status['database'] = 'error'
            health_status['database_error'] = str(e)
        
        return jsonify(health_status)
    
    # Ruta de información del sistema
    @app.route('/system/info')
    def system_info():
        from app.api.v1.endpoints.stats_routes import get_system_stats
        return get_system_stats()
    
    # Manejo de errores
    @app.errorhandler(400)
    def bad_request_error(error):
        return {'error': 'Bad Request', 'message': 'Solicitud incorrecta'}, 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return {'error': 'Unauthorized', 'message': 'Authentication required'}, 401
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not Found', 'message': 'Resource not found'}, 404
    
    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return {'error': 'Method Not Allowed', 'message': 'HTTP method not allowed'}, 405
    
    @app.errorhandler(415)
    def unsupported_media_type_error(error):
        return {'error': 'Bad Request', 'message': 'Content-Type debe ser application/json'}, 400
    
    @app.errorhandler(429)
    def too_many_requests_error(error):
        return {'error': 'Too Many Requests', 'message': 'Rate limit exceeded'}, 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return {'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}, 500
    
    # Middleware para headers de seguridad
    @app.after_request
    def add_security_headers(response):
        if app.config.get('SECURITY_HEADERS'):
            for header, value in app.config['SECURITY_HEADERS'].items():
                response.headers[header] = value
        return response
    
    # Middleware para logging de auditoría
    @app.after_request
    def audit_log(response):
        if app.config.get('AUDIT_LOG_ENABLED') and response.status_code >= 400:
            audit_logger = logging.getLogger('audit')
            audit_logger.info(
                f"Error {response.status_code}: {request.method} {request.path} - "
                f"IP: {request.remote_addr} - User-Agent: {request.headers.get('User-Agent', 'Unknown')}"
            )
        return response
    
    app.logger.info('Aplicación O\'Data POS v2.0.0 creada exitosamente')
    return app

# Importar modelos después de inicializar db
from app.models import user, product, sale, inventory, customer
