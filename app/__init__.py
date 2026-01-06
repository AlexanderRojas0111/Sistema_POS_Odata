"""
Sistema POS O'Data v2.0.2-enterprise - Enterprise Architecture
==============================================================
Arquitectura enterprise con DI Container, Repository Pattern, 
Strategy Pattern y Exception Hierarchy profesional.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import logging
from datetime import datetime

# Inicializar extensiones
db = SQLAlchemy()
cors = CORS()
# Limiter se inicializará con Redis en configure_app
limiter = None

# Versión de la aplicación
APP_VERSION = "2.0.2-enterprise"

def create_app(config_name='production'):
    """Factory pattern para crear aplicación Flask con arquitectura enterprise"""
    app = Flask(__name__)
    
    # Configuración
    configure_app(app, config_name)
    
    # Inicializar extensiones
    db.init_app(app)
    cors.init_app(app)
    
    # Configurar logging después de inicializar la app
    configure_logging(app)
    
    # Configurar limiter con Redis si está disponible
    global limiter
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    redis_url = os.environ.get('REDIS_URL', 'memory://')
    if redis_url.startswith('redis://'):
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            storage_uri=redis_url
        )
    else:
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            storage_uri='memory://'
        )
        app.logger.warning("Using in-memory storage for rate limiting. Not recommended for production.")
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Configurar middleware enterprise
    configure_enterprise_middleware(app)
    
    # Crear tablas
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Failed to create database tables: {e}")
            # Continuar sin crear tablas para evitar que falle la aplicación
        
        # Inicializar sistema de IA
        initialize_ai_system(app)
    
    return app

def configure_app(app, config_name):
    """Configuración centralizada de la aplicación"""
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'enterprise-secret-key-change-in-production'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///pos_odata.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_SORT_KEYS=False,
        JSONIFY_PRETTYPRINT_REGULAR=False,
        RATELIMIT_STORAGE_URL=os.environ.get('REDIS_URL', 'memory://'),
        RATELIMIT_DEFAULT="1000 per hour"
    )

def configure_logging(app):
    """Configuración de logging enterprise"""
    if not app.debug:
        handlers = [logging.StreamHandler()]
        
        # Intentar agregar FileHandler, pero no fallar si no hay permisos
        try:
            # Asegurar que el directorio existe
            import os
            os.makedirs('logs', exist_ok=True)
            handlers.append(logging.FileHandler('logs/app.log'))
        except (PermissionError, OSError) as e:
            app.logger.warning(f"No se pudo crear archivo de log: {e}. Usando solo consola.")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers
        )

def register_blueprints(app):
    """Registrar blueprints de la aplicación"""
    print("DEBUG: Iniciando registro de blueprints...")
    from app.api.v1 import api_bp
    print("DEBUG: api_bp importado exitosamente")
    from app.api.v2 import api_v2_bp
    print("DEBUG: api_v2_bp importado exitosamente")
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(api_v2_bp, url_prefix='/api/v2')

def configure_enterprise_middleware(app):
    """Configurar middleware enterprise"""
    from app.middleware.error_handler import ErrorHandler
    from app.middleware.error_handler_enhanced import error_handler_enhanced
    from app.middleware.request_logger import RequestLogger
    from app.middleware.security_headers import SecurityHeaders
    from app.middleware.validation_middleware import validation_middleware
    from app.monitoring.metrics import monitoring_middleware
    from app.security.rate_limiter import AdvancedRateLimiter
    from app.security.audit_logger import AuditLogger
    
    # Middleware de manejo de errores mejorado
    error_handler_enhanced.init_app(app)
    
    # Middleware de validación
    validation_middleware.init_app(app)
    
    # Middleware de monitoreo
    monitoring_middleware.init_app(app)
    
    # Middleware de logging de requests
    RequestLogger(app)
    
    # Middleware de headers de seguridad
    SecurityHeaders(app)
    
    # Rate limiting avanzado
    AdvancedRateLimiter(app)
    
    # Sistema de auditoría
    app.audit_logger = AuditLogger()
    
    # Configurar DI Container
    configure_di_container(app)

def configure_di_container(app):
    """Configurar DI Container con servicios enterprise"""
    try:
        from app.container import container
        from app.repositories.user_repository import UserRepository
        from app.repositories.product_repository import ProductRepository
        from app.repositories.sale_repository import SaleRepository
        from app.repositories.inventory_repository import InventoryRepository
        from app.services.user_service import UserService
        from app.services.product_service import ProductService
        from app.services.sale_service import SaleService
        from app.services.inventory_service import InventoryService
        
        # Registrar repositories
        container.register_singleton(UserRepository, UserRepository)
        container.register_singleton(ProductRepository, ProductRepository)
        container.register_singleton(SaleRepository, SaleRepository)
        container.register_singleton(InventoryRepository, InventoryRepository)
        
        # Registrar services
        container.register_singleton(UserService, UserService)
        container.register_singleton(ProductService, ProductService)
        container.register_singleton(SaleService, SaleService)
        container.register_singleton(InventoryService, InventoryService)
        
        # Hacer container disponible en la app
        app.container = container
        
        app.logger.info("DI Container configured with enterprise services")
    except Exception as e:
        app.logger.error(f"Failed to configure DI Container: {e}")
        # Continuar sin DI Container para evitar que falle la aplicación
        app.container = None

def initialize_ai_system(app):
    """Inicializar sistema de IA al arrancar la aplicación"""
    try:
        from app.services.ai_service import AIService
        from app.models.product import Product
        
        # Verificar si hay productos para entrenar
        product_count = Product.query.filter(Product.is_active == True).count()
        
        if product_count > 0:
            ai_service = AIService()
            success = ai_service.initialize_ai_system()
            
            if success:
                app.logger.info(f"AI system initialized successfully with {product_count} products")
            else:
                app.logger.warning("AI system initialization failed")
        else:
            app.logger.info("No products found for AI initialization")
            
    except Exception as e:
        app.logger.error(f"Error initializing AI system: {e}")
