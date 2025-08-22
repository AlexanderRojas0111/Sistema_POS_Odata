from flask_sqlalchemy import SQLAlchemy
from contextlib import contextmanager

# Instancia de SQLAlchemy
db = SQLAlchemy()

# Definir Base para los modelos
Base = db.Model

@contextmanager
def db_session():
    """Proporciona un contexto para las operaciones de base de datos"""
    session = db.session
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def init_db(app):
    """Inicializa la base de datos con la aplicación"""
    db.init_app(app)
    
    with app.app_context():
        # Importar modelos aquí para evitar importaciones circulares
        from app.models.user import User
        from app.models.product import Product
        from app.models.inventory import Inventory
        from app.models.sale import Sale
        from app.models.customer import Customer
        
        # Crear todas las tablas
        db.create_all() 