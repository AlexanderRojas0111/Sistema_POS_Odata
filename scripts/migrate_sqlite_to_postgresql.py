#!/usr/bin/env python3
"""
Migración de SQLite a PostgreSQL - O'Data v2.0.0
================================================

Script para migrar datos y esquema de SQLite a PostgreSQL

Autor: Sistema POS Odata
Versión: 2.0.0
"""

import os
import sys
import sqlite3
import psycopg2
import argparse
import logging
from datetime import datetime
from pathlib import Path


class SQLiteToPostgreSQLMigrator:
    """Clase para migrar de SQLite a PostgreSQL"""
    
    def __init__(self, sqlite_path, config_file):
        self.sqlite_path = Path(sqlite_path)
        self.config_file = Path(config_file)
        self.sqlite_conn = None
        self.pg_conn = None
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Cargar configuración de PostgreSQL"""
        try:
            # Cargar variables de entorno
            from dotenv import load_dotenv
            load_dotenv(self.config_file)
            
            self.pg_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'database': os.getenv('DB_NAME', 'odata_pos'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', ''),
                'sslmode': os.getenv('DB_SSLMODE', 'prefer')
            }
            
            self.logger.info("✅ Configuración cargada correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error cargando configuración: {e}")
            return False
    
    def connect_sqlite(self):
        """Conectar a SQLite"""
        try:
            if not self.sqlite_path.exists():
                self.logger.error(f"❌ Archivo SQLite no encontrado: {self.sqlite_path}")
                return False
            
            self.sqlite_conn = sqlite3.connect(str(self.sqlite_path))
            self.logger.info("✅ Conexión a SQLite establecida")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error conectando a SQLite: {e}")
            return False
    
    def connect_postgresql(self):
        """Conectar a PostgreSQL"""
        try:
            self.pg_conn = psycopg2.connect(**self.pg_config)
            self.logger.info("✅ Conexión a PostgreSQL establecida")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error conectando a PostgreSQL: {e}")
            return False
    
    def create_database(self):
        """Crear base de datos PostgreSQL si no existe"""
        try:
            # Conectar a postgres para crear la base de datos
            temp_config = self.pg_config.copy()
            temp_config['database'] = 'postgres'
            
            with psycopg2.connect(**temp_config) as temp_conn:
                temp_conn.autocommit = True
                with temp_conn.cursor() as cursor:
                    # Verificar si la base de datos existe
                    cursor.execute(
                        "SELECT 1 FROM pg_database WHERE datname = %s",
                        (self.pg_config['database'],)
                    )
                    
                    if not cursor.fetchone():
                        cursor.execute(
                            f"CREATE DATABASE {self.pg_config['database']}"
                        )
                        self.logger.info(f"✅ Base de datos {self.pg_config['database']} creada")
                    else:
                        self.logger.info(f"✅ Base de datos {self.pg_config['database']} ya existe")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error creando base de datos: {e}")
            return False
    
    def get_sqlite_schema(self):
        """Obtener esquema de SQLite"""
        try:
            cursor = self.sqlite_conn.cursor()
            
            # Obtener todas las tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            schema = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                schema[table_name] = columns
            
            self.logger.info(f"✅ Esquema de SQLite obtenido: {len(schema)} tablas")
            return schema
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo esquema: {e}")
            return None
    
    def convert_sqlite_type(self, sqlite_type):
        """Convertir tipo de SQLite a PostgreSQL"""
        type_mapping = {
            'INTEGER': 'INTEGER',
            'REAL': 'DOUBLE PRECISION',
            'TEXT': 'TEXT',
            'BLOB': 'BYTEA',
            'BOOLEAN': 'BOOLEAN',
            'DATETIME': 'TIMESTAMP',
            'DATE': 'DATE',
            'TIME': 'TIME'
        }
        
        sqlite_type = sqlite_type.upper()
        for key, value in type_mapping.items():
            if key in sqlite_type:
                return value
        
        return 'TEXT'  # Tipo por defecto
    
    def create_postgresql_schema(self, schema):
        """Crear esquema en PostgreSQL"""
        try:
            cursor = self.pg_conn.cursor()
            
            for table_name, columns in schema.items():
                # Crear tabla
                column_definitions = []
                for col in columns:
                    col_id, col_name, col_type, not_null, default_val, pk = col
                    
                    pg_type = self.convert_sqlite_type(col_type)
                    definition = f"{col_name} {pg_type}"
                    
                    if not_null:
                        definition += " NOT NULL"
                    
                    if pk:
                        definition += " PRIMARY KEY"
                    
                    column_definitions.append(definition)
                
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {', '.join(column_definitions)}
                )
                """
                
                cursor.execute(create_table_sql)
                self.logger.info(f"✅ Tabla {table_name} creada")
            
            self.pg_conn.commit()
            self.logger.info("✅ Esquema de PostgreSQL creado")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error creando esquema: {e}")
            self.pg_conn.rollback()
            return False
    
    def migrate_data(self, schema):
        """Migrar datos de SQLite a PostgreSQL"""
        try:
            sqlite_cursor = self.sqlite_conn.cursor()
            pg_cursor = self.pg_conn.cursor()
            
            total_records = 0
            
            for table_name, columns in schema.items():
                # Obtener datos de SQLite
                sqlite_cursor.execute(f"SELECT * FROM {table_name}")
                rows = sqlite_cursor.fetchall()
                
                if not rows:
                    self.logger.info(f"⚠️  Tabla {table_name} está vacía")
                    continue
                
                # Preparar INSERT para PostgreSQL
                column_names = [col[1] for col in columns]
                placeholders = ', '.join(['%s'] * len(column_names))
                insert_sql = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
                
                # Migrar datos en lotes
                batch_size = 1000
                for i in range(0, len(rows), batch_size):
                    batch = rows[i:i + batch_size]
                    pg_cursor.executemany(insert_sql, batch)
                    
                    self.logger.info(f"📦 Lote migrado: {table_name} - {len(batch)} registros")
                
                total_records += len(rows)
                self.logger.info(f"✅ Tabla {table_name} migrada: {len(rows)} registros")
            
            self.pg_conn.commit()
            self.logger.info(f"✅ Migración completada: {total_records} registros totales")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error migrando datos: {e}")
            self.pg_conn.rollback()
            return False
    
    def create_indexes(self):
        """Crear índices esenciales en PostgreSQL"""
        try:
            cursor = self.pg_conn.cursor()
            
            # Índices básicos para rendimiento
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_products_code ON products(code)",
                "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
                "CREATE INDEX IF NOT EXISTS idx_sales_user_id ON sales(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_sales_created_at ON sales(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX IF NOT EXISTS idx_inventory_product_id ON inventory(product_id)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            self.pg_conn.commit()
            self.logger.info("✅ Índices creados")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error creando índices: {e}")
            self.pg_conn.rollback()
            return False
    
    def verify_migration(self, schema):
        """Verificar que la migración fue exitosa"""
        try:
            sqlite_cursor = self.sqlite_conn.cursor()
            pg_cursor = self.pg_conn.cursor()
            
            verification_results = {}
            
            for table_name in schema.keys():
                # Contar registros en SQLite
                sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                sqlite_count = sqlite_cursor.fetchone()[0]
                
                # Contar registros en PostgreSQL
                pg_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                pg_count = pg_cursor.fetchone()[0]
                
                verification_results[table_name] = {
                    'sqlite': sqlite_count,
                    'postgresql': pg_count,
                    'match': sqlite_count == pg_count
                }
                
                status = "✅" if sqlite_count == pg_count else "❌"
                self.logger.info(f"{status} {table_name}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
            
            # Resumen
            total_tables = len(verification_results)
            matching_tables = sum(1 for r in verification_results.values() if r['match'])
            
            self.logger.info(f"📊 Verificación completada: {matching_tables}/{total_tables} tablas coinciden")
            
            return matching_tables == total_tables
            
        except Exception as e:
            self.logger.error(f"❌ Error verificando migración: {e}")
            return False
    
    def cleanup(self):
        """Limpiar conexiones"""
        try:
            if self.sqlite_conn:
                self.sqlite_conn.close()
            if self.pg_conn:
                self.pg_conn.close()
            self.logger.info("🧹 Conexiones cerradas")
        except Exception as e:
            self.logger.error(f"⚠️  Error cerrando conexiones: {e}")
    
    def run(self, dry_run=False):
        """Ejecutar migración completa"""
        try:
            self.logger.info("🚀 Iniciando migración de SQLite a PostgreSQL")
            self.logger.info("=" * 60)
            
            if dry_run:
                self.logger.info("🔍 MODO DRY RUN - No se realizarán cambios")
            
            # Cargar configuración
            if not self.load_config():
                return False
            
            # Conectar a SQLite
            if not self.connect_sqlite():
                return False
            
            # Conectar a PostgreSQL
            if not self.connect_postgresql():
                return False
            
            # Crear base de datos si no existe
            if not self.create_database():
                return False
            
            # Obtener esquema de SQLite
            schema = self.get_sqlite_schema()
            if not schema:
                return False
            
            if dry_run:
                self.logger.info("🔍 DRY RUN: Esquema obtenido, no se creará en PostgreSQL")
                return True
            
            # Crear esquema en PostgreSQL
            if not self.create_postgresql_schema(schema):
                return False
            
            # Migrar datos
            if not self.migrate_data(schema):
                return False
            
            # Crear índices
            if not self.create_indexes():
                return False
            
            # Verificar migración
            if not self.verify_migration(schema):
                self.logger.warning("⚠️  La migración puede no estar completa")
            
            self.logger.info("🎉 Migración completada exitosamente!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error durante la migración: {e}")
            return False
        
        finally:
            self.cleanup()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Migrar de SQLite a PostgreSQL para O'Data POS v2.0.0"
    )
    
    parser.add_argument(
        'sqlite_path',
        help='Ruta al archivo SQLite'
    )
    
    parser.add_argument(
        'config_file',
        help='Archivo de configuración (.env)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Ejecutar en modo dry run (sin cambios)'
    )
    
    args = parser.parse_args()
    
    # Verificar archivos
    if not Path(args.sqlite_path).exists():
        print(f"❌ Archivo SQLite no encontrado: {args.sqlite_path}")
        sys.exit(1)
    
    if not Path(args.config_file).exists():
        print(f"❌ Archivo de configuración no encontrado: {args.config_file}")
        sys.exit(1)
    
    # Ejecutar migración
    migrator = SQLiteToPostgreSQLMigrator(args.sqlite_path, args.config_file)
    success = migrator.run(dry_run=args.dry_run)
    
    if success:
        print("\n✅ Migración completada exitosamente")
        sys.exit(0)
    else:
        print("\n❌ Error en la migración")
        sys.exit(1)


if __name__ == "__main__":
    main()
