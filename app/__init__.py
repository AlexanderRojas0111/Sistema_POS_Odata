from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restx import Api

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Documentación OpenAPI
    api = Api(app, version='1.0', title='Inventario API', description='Documentación de la API de Inventario', doc='/docs')

    # Importa y registra los blueprints de tus módulos
    from app.routes.products import products_bp
    from app.routes.sales import sales_bp
    from app.routes.inventory import inventory_bp
    from app.routes.users import users_bp
    # from app.routes.reports import reports_bp

    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(sales_bp, url_prefix='/api/sales')
    app.register_blueprint(inventory_bp, url_prefix='/api/inventory')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    # app.register_blueprint(reports_bp, url_prefix='/api/reports')

    return app
