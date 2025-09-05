#!/usr/bin/env python3
"""
Configuración de PostgreSQL - O'Data v2.0.0
===========================================

Configuración para:
- Conexión a PostgreSQL
- Migraciones con Alembic
- Optimización de queries
- Pool de conexiones

Autor: Sistema POS Odata
Versión: 2.0.0
"""

import os
import logging
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from alembic import command
from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic.util.exc import CommandError
import psycopg2
from psycopg2.extras import RealDictCursor
import time

logger = logging.getLogger(__name__)

class PostgreSQLManager:
    """Gestor de conexiones y operaciones PostgreSQL"""
    
    def __init__(self, app=None):
        self.app = app
        self.engine: Optional[Engine] = None
        self.alembic_cfg: Optional[AlembicConfig] = None
        self.is_connected = False
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar PostgreSQL con la aplicación Flask"""
        self.app = app
        
        # Configuración de PostgreSQL
        postgres_config = {
            'host': app.config.get('DB_HOST', 'localhost'),
            'port': app.config.get('DB_PORT', 5432),
            'database': app.config.get('DB_NAME', 'odata_pos'),
            'user': app.config.get('DB_USER', 'odata_user'),
            'password': app.config.get('DB_PASSWORD', 'odata_password'),
            'sslmode': app.config.get('DB_SSLMODE', 'prefer'),
            'connect_timeout': 10,
            'application_name': 'OData_POS_v2'
        }
        
        try:
            # Crear engine con configuración optimizada
            self.engine = create_engine(
                f"postgresql://{postgres_config['user']}:{postgres_config['password']}@"
                f"{postgres_config['host']}:{postgres_config['port']}/{postgres_config['database']}",
                poolclass=QueuePool,
                pool_size=app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}).get('pool_size', 20),
                max_overflow=app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}).get('max_overflow', 10),
                pool_pre_ping=app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}).get('pool_pre_ping', True),
                pool_recycle=app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}).get('pool_recycle', 300),
                pool_timeout=app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}).get('pool_timeout', 20),
                echo=app.config.get('DEBUG', False),
                echo_pool=app.config.get('DEBUG', False)
            )
            
            # Configurar eventos del engine
            self._setup_engine_events()
            
            # Verificar conexión
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.is_connected = True
            logger.info(f"PostgreSQL conectado exitosamente en {postgres_config['host']}:{postgres_config['port']}")
            
            # Inicializar Alembic
            self._init_alembic()
            
        except Exception as e:
            logger.error(f"Error conectando a PostgreSQL: {e}")
            self.is_connected = False
            self.engine = None
    
    def _setup_engine_events(self):
        """Configurar eventos del engine para logging y optimización"""
        
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault('query_start_time', []).append(time.time())
        
        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - conn.info['query_start_time'].pop(-1)
            if total > 1.0:  # Log queries lentos (>1 segundo)
                logger.warning(f"Query lento ({total:.2f}s): {statement[:100]}...")
    
    def _init_alembic(self):
        """Inicializar configuración de Alembic"""
        try:
            # Buscar archivo alembic.ini
            alembic_ini_path = os.path.join(os.getcwd(), 'migrations', 'alembic.ini')
            if os.path.exists(alembic_ini_path):
                self.alembic_cfg = AlembicConfig(alembic_ini_path)
                self.alembic_cfg.set_main_option('script_location', 'migrations')
                self.alembic_cfg.set_main_option('sqlalchemy.url', str(self.engine.url))
                logger.info("Alembic configurado correctamente")
            else:
                logger.warning("Archivo alembic.ini no encontrado")
        except Exception as e:
            logger.error(f"Error configurando Alembic: {e}")
    
    def get_connection(self):
        """Obtener conexión directa a PostgreSQL"""
        if not self.is_connected or not self.engine:
            return None
        
        try:
            return self.engine.connect()
        except Exception as e:
            logger.error(f"Error obteniendo conexión: {e}")
            return None
    
    def execute_query(self, query: str, params: Dict[str, Any] = None) -> Optional[list]:
        """Ejecutar query SQL personalizada"""
        if not self.is_connected or not self.engine:
            return None
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                if result.returns_rows:
                    return [dict(row) for row in result]
                return None
        except Exception as e:
            logger.error(f"Error ejecutando query: {e}")
            return None
    
    def get_database_info(self) -> Dict[str, Any]:
        """Obtener información de la base de datos"""
        if not self.is_connected or not self.engine:
            return {}
        
        try:
            with self.engine.connect() as conn:
                # Información de la base de datos
                db_info = conn.execute(text("""
                    SELECT 
                        current_database() as database_name,
                        current_user as current_user,
                        version() as version,
                        pg_size_pretty(pg_database_size(current_database())) as size
                """)).fetchone()
                
                # Estadísticas de conexiones
                connections = conn.execute(text("""
                    SELECT 
                        count(*) as active_connections,
                        count(*) FILTER (WHERE state = 'active') as active_queries
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """)).fetchone()
                
                # Información de tablas
                tables = conn.execute(text("""
                    SELECT 
                        schemaname,
                        tablename,
                        n_tup_ins as inserts,
                        n_tup_upd as updates,
                        n_tup_del as deletes,
                        n_live_tup as live_rows,
                        n_dead_tup as dead_rows
                    FROM pg_stat_user_tables 
                    ORDER BY n_live_tup DESC
                """)).fetchall()
                
                return {
                    'database': dict(db_info),
                    'connections': dict(connections),
                    'tables': [dict(table) for table in tables]
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo información de BD: {e}")
            return {}
    
    def run_migrations(self, target: str = 'head') -> bool:
        """Ejecutar migraciones de Alembic"""
        if not self.alembic_cfg:
            logger.error("Alembic no configurado")
            return False
        
        try:
            command.upgrade(self.alembic_cfg, target)
            logger.info(f"Migraciones ejecutadas hasta: {target}")
            return True
        except CommandError as e:
            logger.error(f"Error ejecutando migraciones: {e}")
            return False
    
    def create_migration(self, message: str) -> bool:
        """Crear nueva migración"""
        if not self.alembic_cfg:
            logger.error("Alembic no configurado")
            return False
        
        try:
            command.revision(self.alembic_cfg, message=message, autogenerate=True)
            logger.info(f"Nueva migración creada: {message}")
            return True
        except CommandError as e:
            logger.error(f"Error creando migración: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Obtener estado de las migraciones"""
        if not self.alembic_cfg:
            return {}
        
        try:
            script_dir = ScriptDirectory.from_config(self.alembic_cfg)
            with self.engine.connect() as conn:
                context = MigrationContext.configure(conn)
                current_rev = context.get_current_revision()
                head_rev = script_dir.get_current_head()
                
                # Obtener historial de migraciones
                history = []
                for rev in script_dir.walk_revisions():
                    history.append({
                        'revision': rev.revision,
                        'down_revision': rev.down_revision,
                        'message': rev.message,
                        'is_current': rev.revision == current_rev,
                        'is_head': rev.revision == head_rev
                    })
                
                return {
                    'current_revision': current_rev,
                    'head_revision': head_rev,
                    'is_up_to_date': current_rev == head_rev,
                    'pending_migrations': len([h for h in history if not h['is_current'] and h['revision'] != head_rev]),
                    'history': history
                }
                
        except Exception as e:
            logger.error(f"Error obteniendo estado de migraciones: {e}")
            return {}
    
    def optimize_database(self) -> bool:
        """Optimizar base de datos"""
        if not self.is_connected or not self.engine:
            return False
        
        try:
            with self.engine.connect() as conn:
                # Analizar tablas
                conn.execute(text("ANALYZE"))
                
                # Vacuum (solo si es necesario)
                conn.execute(text("VACUUM ANALYZE"))
                
                # Reindexar si es necesario
                conn.execute(text("REINDEX DATABASE current_database()"))
                
                logger.info("Base de datos optimizada")
                return True
                
        except Exception as e:
            logger.error(f"Error optimizando BD: {e}")
            return False
    
    def backup_database(self, backup_path: str) -> bool:
        """Crear backup de la base de datos"""
        if not self.is_connected:
            return False
        
        try:
            # Usar pg_dump para crear backup
            import subprocess
            
            db_url = str(self.engine.url)
            db_parts = db_url.replace('postgresql://', '').split('@')
            user_pass = db_parts[0].split(':')
            host_db = db_parts[1].split('/')
            
            cmd = [
                'pg_dump',
                '-h', host_db[0].split(':')[0],
                '-p', host_db[0].split(':')[1] if ':' in host_db[0] else '5432',
                '-U', user_pass[0],
                '-d', host_db[1],
                '-f', backup_path,
                '--verbose',
                '--no-password'
            ]
            
            # Establecer variable de entorno para password
            env = os.environ.copy()
            env['PGPASSWORD'] = user_pass[1]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Backup creado exitosamente en: {backup_path}")
                return True
            else:
                logger.error(f"Error en backup: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return False

# Instancia global
postgresql_manager = PostgreSQLManager()

def get_postgresql_connection():
    """Obtener conexión a PostgreSQL"""
    return postgresql_manager.get_connection()

def execute_custom_query(query: str, params: Dict[str, Any] = None) -> Optional[list]:
    """Ejecutar query personalizada"""
    return postgresql_manager.execute_query(query, params)

def get_db_info() -> Dict[str, Any]:
    """Obtener información de la base de datos"""
    return postgresql_manager.get_database_info()
