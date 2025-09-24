import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from config import Config

def setup_vector_db():
    """Configura la base de datos vectorial con pgvector"""
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres")
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Crear cursor
        cur = conn.cursor()
        
        # Crear base de datos si no existe
        db_name = Config.VECTOR_DATABASE_URL.split('/')[-1]
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_name}'")
        exists = cur.fetchone()
        if not exists:
            cur.execute(f'CREATE DATABASE {db_name}')
            print(f"Base de datos '{db_name}' creada.")
        
        # Conectar a la base de datos creada
        conn.close()
        conn = psycopg2.connect(
            host="localhost",
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            database=db_name
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Instalar extensión pgvector
        cur.execute('CREATE EXTENSION IF NOT EXISTS vector')
        print("Extensión pgvector instalada.")
        
        # Cerrar conexiones
        cur.close()
        conn.close()
        print("Configuración completada exitosamente.")
        
    except Exception as e:
        print(f"Error durante la configuración: {str(e)}")
        raise

if __name__ == '__main__':
    setup_vector_db() 