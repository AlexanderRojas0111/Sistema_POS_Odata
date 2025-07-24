from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from app.database import db
import os

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Asegurar que el directorio instance existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Cargar configuración
    if test_config is None:
        app.config.from_object('config.Config')
        # Cargar configuración de .env si existe
        app.config.from_prefixed_env()
    else:
        app.config.update(test_config)
    
    # Inicializar extensiones
    CORS(app)
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    
    # Registrar blueprints
    from app.routes.products import products
    from app.routes.sales import sales
    from app.routes.inventory import inventory
    from app.routes.users import users
    from app.routes.customers import customers
    from app.routes.semantic_search import semantic_search
    from app.routes.agents import agents
    
    app.register_blueprint(products)
    app.register_blueprint(sales)
    app.register_blueprint(inventory)
    app.register_blueprint(users)
    app.register_blueprint(customers)
    app.register_blueprint(semantic_search)
    app.register_blueprint(agents)
    
    return app
