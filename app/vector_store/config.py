from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Usar variable de entorno o valor por defecto
VECTOR_DATABASE_URL = os.getenv('VECTOR_DATABASE_URL', 'postgresql://localhost/vector_db')

engine = create_engine(VECTOR_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
VectorBase = declarative_base()

def get_vector_db():
    """Obtiene una sesión de la base de datos vectorial"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 