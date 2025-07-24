from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.database import db
import os

def create_app(test_config=None):
    app = Flask(__name__)
    CORS(app)
    
    if test_config is None:
        app.config.from_object('config.Config')
    else:
        app.config.update(test_config)
    
    # Inicializar base de datos principal
    db.init_app(app)
    
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
    
    # Crear tablas
    with app.app_context():
        db.create_all()
        
        # Inicializar base de datos vectorial
        from app.vector_store.models import ProductEmbedding, DocumentEmbedding
        from app.vector_store.config import VectorBase, engine
        VectorBase.metadata.create_all(bind=engine)
    
    return app
