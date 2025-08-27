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
        try:
            from app.models import User, Product, Inventory, Sale, Customer
            # Crear todas las tablas
            db.create_all()
        except ImportError as e:
            app.logger.warning(f"Error importando modelos: {e}. Las tablas se crearán cuando se importen los modelos.") 