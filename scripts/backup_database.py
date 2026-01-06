#!/usr/bin/env python3
"""
Script de Backup Automático de Base de Datos
Sistema POS O'Data v2.0.2-enterprise
====================================
Realiza backups automáticos de PostgreSQL con rotación y compresión.
"""

import sys
import os
import subprocess
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app

def create_backup(backup_dir: str = "/app/backups", retention_days: int = 30) -> Optional[str]:
    """Crear backup de la base de datos"""
    app = create_app('production')
    
    with app.app_context():
        # Obtener configuración de la base de datos
        db_url = os.environ.get('DATABASE_URL', '')
        if not db_url:
            print("❌ Error: DATABASE_URL no configurada")
            return None
        
        # Parsear DATABASE_URL
        # Formato: postgresql://user:password@host:port/database
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        
        db_user = parsed.username
        db_password = parsed.password
        db_host = parsed.hostname
        db_port = parsed.port or 5432
        db_name = parsed.path.lstrip('/')
        
        # Crear directorio de backups si no existe
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Nombre del archivo de backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"pos_odata_backup_{timestamp}.sql"
        backup_file_gz = backup_path / f"pos_odata_backup_{timestamp}.sql.gz"
        
        try:
            # Crear backup usando pg_dump
            print(f"📦 Creando backup: {backup_file.name}")
            
            # Configurar variables de entorno para pg_dump
            env = os.environ.copy()
            env['PGPASSWORD'] = db_password
            
            # Ejecutar pg_dump usando docker exec si estamos en contenedor
            # O usar pg_dump directamente si está disponible
            import shutil
            pg_dump_path = shutil.which('pg_dump')
            
            if not pg_dump_path:
                # Si pg_dump no está disponible, usar docker exec
                print("⚠️  pg_dump no disponible en el contenedor")
                print("   Usando método alternativo: docker exec")
                # El backup se debe hacer desde el host usando docker exec
                return None
            
            cmd = [
                pg_dump_path,
                '-h', db_host,
                '-p', str(db_port),
                '-U', db_user,
                '-d', db_name,
                '-F', 'c',  # Formato custom (binario)
                '-f', str(backup_file)
            ]
            
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Error ejecutando pg_dump: {result.stderr}")
                return None
            
            # Comprimir backup
            print(f"🗜️  Comprimiendo backup...")
            with open(backup_file, 'rb') as f_in:
                with gzip.open(backup_file_gz, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Eliminar archivo sin comprimir
            backup_file.unlink()
            
            # Obtener tamaño del archivo
            file_size = backup_file_gz.stat().st_size / (1024 * 1024)  # MB
            
            print(f"✅ Backup creado exitosamente: {backup_file_gz.name}")
            print(f"   Tamaño: {file_size:.2f} MB")
            
            # Limpiar backups antiguos
            cleanup_old_backups(backup_path, retention_days)
            
            return str(backup_file_gz)
            
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return None

def cleanup_old_backups(backup_dir: Path, retention_days: int):
    """Eliminar backups más antiguos que retention_days"""
    try:
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        backups_deleted = 0
        for backup_file in backup_dir.glob("pos_odata_backup_*.sql.gz"):
            # Extraer fecha del nombre del archivo
            try:
                timestamp_str = backup_file.stem.replace('pos_odata_backup_', '').replace('.sql', '')
                file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                
                if file_date < cutoff_date:
                    backup_file.unlink()
                    backups_deleted += 1
            except ValueError:
                # Si no se puede parsear la fecha, mantener el archivo
                continue
        
        if backups_deleted > 0:
            print(f"🗑️  Eliminados {backups_deleted} backups antiguos")
            
    except Exception as e:
        print(f"⚠️  Error limpiando backups antiguos: {e}")

def list_backups(backup_dir: str = "/app/backups"):
    """Listar backups disponibles"""
    backup_path = Path(backup_dir)
    
    if not backup_path.exists():
        print("❌ Directorio de backups no existe")
        return
    
    backups = sorted(backup_path.glob("pos_odata_backup_*.sql.gz"), reverse=True)
    
    if not backups:
        print("📭 No hay backups disponibles")
        return
    
    print(f"📋 Backups disponibles ({len(backups)}):")
    print("-" * 60)
    
    for backup in backups:
        file_size = backup.stat().st_size / (1024 * 1024)  # MB
        file_date = datetime.fromtimestamp(backup.stat().st_mtime)
        
        print(f"  {backup.name}")
        print(f"    Tamaño: {file_size:.2f} MB")
        print(f"    Fecha: {file_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup de base de datos PostgreSQL')
    parser.add_argument('--backup-dir', default='/app/backups', help='Directorio de backups')
    parser.add_argument('--retention-days', type=int, default=30, help='Días de retención')
    parser.add_argument('--list', action='store_true', help='Listar backups disponibles')
    
    args = parser.parse_args()
    
    if args.list:
        list_backups(args.backup_dir)
    else:
        print("=" * 60)
        print("BACKUP DE BASE DE DATOS")
        print("Sistema POS O'Data v2.0.2-enterprise")
        print("=" * 60)
        print()
        
        backup_file = create_backup(args.backup_dir, args.retention_days)
        
        if backup_file:
            print(f"\n✅ Backup completado: {backup_file}")
            sys.exit(0)
        else:
            print("\n❌ Backup falló")
            sys.exit(1)
