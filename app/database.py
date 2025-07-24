from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Inicializa la base de datos con la aplicación"""
    db.init_app(app)
    
    with app.app_context():
        # Importar modelos aquí para evitar importaciones circulares
        from app.models import Product, User, Customer, Sale, Inventory, ProductEmbedding, DocumentEmbedding
        
        # Crear todas las tablas
        db.create_all() 