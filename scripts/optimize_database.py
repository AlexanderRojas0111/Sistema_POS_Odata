#!/usr/bin/env python3
"""
Script de Optimización Avanzada de Base de Datos
Sistema POS O'Data v2.0.2-enterprise
====================================
Aplica optimizaciones avanzadas a la base de datos PostgreSQL.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def optimize_database():
    """Aplicar optimizaciones avanzadas a la base de datos"""
    print("=" * 70)
    print("OPTIMIZACIÓN AVANZADA DE BASE DE DATOS")
    print("Sistema POS O'Data v2.0.2-enterprise")
    print("=" * 70)
    print()
    
    app = create_app()
    
    with app.app_context():
        # Obtener URL de conexión
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL no configurada")
            return False
        
        # Parsear URL para obtener parámetros
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        
        # Conectar directamente a PostgreSQL
        conn = psycopg2.connect(
            host=parsed.hostname or 'localhost',
            port=parsed.port or 5432,
            user=parsed.username or 'pos_user',
            password=parsed.password,
            database=parsed.path.lstrip('/') or 'pos_odata'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("📊 Aplicando optimizaciones...")
        print("-" * 70)
        
        optimizations = [
            ("ANALYZE", "Actualizar estadísticas de tablas"),
            ("VACUUM ANALYZE", "Limpiar y analizar base de datos"),
            ("REINDEX", "Reconstruir índices"),
        ]
        
        results = []
        
        for command, description in optimizations:
            try:
                print(f"   {description}...", end=" ")
                if command == "ANALYZE":
                    cur.execute("ANALYZE;")
                elif command == "VACUUM ANALYZE":
                    cur.execute("VACUUM ANALYZE;")
                elif command == "REINDEX":
                    cur.execute("REINDEX DATABASE pos_odata;")
                
                results.append((description, True, "OK"))
                print("✅")
            except Exception as e:
                results.append((description, False, str(e)))
                print(f"❌ Error: {e}")
        
        print()
        print("📈 Verificando índices críticos...")
        print("-" * 70)
        
        # Verificar índices importantes
        critical_indexes = [
            ('users', 'username'),
            ('users', 'email'),
            ('products', 'sku'),
            ('sales', 'created_at'),
            ('inventory', 'product_id'),
        ]
        
        for table, column in critical_indexes:
            try:
                cur.execute("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE tablename = %s 
                    AND indexdef LIKE %s
                """, (table, f'%{column}%'))
                
                indexes = cur.fetchall()
                if indexes:
                    print(f"   ✅ {table}.{column}: {len(indexes)} índice(s)")
                else:
                    print(f"   ⚠️  {table}.{column}: Sin índice")
            except Exception as e:
                print(f"   ❌ {table}.{column}: Error - {e}")
        
        print()
        print("📊 Estadísticas de la base de datos:")
        print("-" * 70)
        
        # Obtener estadísticas
        stats_queries = [
            ("Total de tablas", "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"),
            ("Total de índices", "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public'"),
            ("Tamaño de la base de datos", "SELECT pg_size_pretty(pg_database_size('pos_odata'))"),
            ("Conexiones activas", "SELECT COUNT(*) FROM pg_stat_activity WHERE datname = 'pos_odata'"),
        ]
        
        for stat_name, query in stats_queries:
            try:
                cur.execute(query)
                result = cur.fetchone()
                print(f"   {stat_name}: {result[0]}")
            except Exception as e:
                print(f"   {stat_name}: Error - {e}")
        
        cur.close()
        conn.close()
        
        print()
        print("=" * 70)
        print("✅ Optimización completada")
        
        return True

if __name__ == '__main__':
    success = optimize_database()
    sys.exit(0 if success else 1)

