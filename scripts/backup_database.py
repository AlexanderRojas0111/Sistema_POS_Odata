#!/usr/bin/env python3
"""
Script de Backup Automático - Sistema POS Sabrositas v2.0.0
===========================================================
Backup automático de base de datos PostgreSQL multi-tienda
"""

import os
import subprocess
import datetime
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Servicio de backup automático de base de datos"""
    
    def __init__(self):
        self.backup_dir = Path(os.environ.get('BACKUP_DIR', '/backups'))
        self.database_url = os.environ.get('DATABASE_URL', '')
        self.retention_days = int(os.environ.get('BACKUP_RETENTION_DAYS', '30'))
        self.max_files = int(os.environ.get('BACKUP_MAX_FILES', '50'))
        
        # Crear directorio de backup si no existe
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self):
        """Crear backup de la base de datos"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"pos_sabrositas_backup_{timestamp}.sql"
            backup_path = self.backup_dir / backup_filename
            
            logger.info(f"Iniciando backup: {backup_filename}")
            
            # Comando pg_dump
            cmd = [
                'pg_dump',
                '--host=pos-postgres-production',
                '--port=5432',
                '--username=pos_user',
                '--dbname=pos_odata',
                '--verbose',
                '--clean',
                '--if-exists',
                '--create',
                '--format=plain',
                f'--file={backup_path}'
            ]
            
            # Ejecutar backup
            result = subprocess.run(
                cmd,
                env={**os.environ, 'PGPASSWORD': os.environ.get('POSTGRES_PASSWORD', '')},
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Backup completado exitosamente: {backup_filename}")
                
                # Comprimir backup
                self._compress_backup(backup_path)
                
                # Limpiar backups antiguos
                self._cleanup_old_backups()
                
                # Crear archivo de estado
                self._create_status_file(backup_filename, True)
                
                return True
            else:
                logger.error(f"Error en backup: {result.stderr}")
                self._create_status_file(backup_filename, False, result.stderr)
                return False
                
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return False
    
    def _compress_backup(self, backup_path: Path):
        """Comprimir archivo de backup"""
        try:
            compressed_path = backup_path.with_suffix('.sql.gz')
            
            cmd = ['gzip', str(backup_path)]
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0:
                logger.info(f"Backup comprimido: {compressed_path.name}")
            else:
                logger.warning("Error comprimiendo backup")
                
        except Exception as e:
            logger.warning(f"Error comprimiendo backup: {e}")
    
    def _cleanup_old_backups(self):
        """Limpiar backups antiguos"""
        try:
            # Obtener todos los archivos de backup
            backup_files = list(self.backup_dir.glob("pos_sabrositas_backup_*.sql*"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Eliminar por cantidad máxima
            if len(backup_files) > self.max_files:
                files_to_delete = backup_files[self.max_files:]
                for file_path in files_to_delete:
                    file_path.unlink()
                    logger.info(f"Backup eliminado por límite de cantidad: {file_path.name}")
            
            # Eliminar por antigüedad
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.retention_days)
            
            for file_path in backup_files:
                file_time = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_date:
                    file_path.unlink()
                    logger.info(f"Backup eliminado por antigüedad: {file_path.name}")
            
        except Exception as e:
            logger.warning(f"Error limpiando backups antiguos: {e}")
    
    def _create_status_file(self, backup_name: str, success: bool, error_msg: str = None):
        """Crear archivo de estado del último backup"""
        try:
            status_file = self.backup_dir / 'last_backup.log'
            
            status_data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'backup_name': backup_name,
                'success': success,
                'error_message': error_msg if error_msg else None
            }
            
            with open(status_file, 'w') as f:
                import json
                json.dump(status_data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Error creando archivo de estado: {e}")
    
    def verify_backup(self, backup_path: Path):
        """Verificar integridad del backup"""
        try:
            if not backup_path.exists():
                return False
            
            # Verificar que el archivo no esté vacío
            if backup_path.stat().st_size == 0:
                return False
            
            # Verificar contenido básico del SQL
            with open(backup_path, 'r') as f:
                content = f.read(1000)  # Leer primeros 1000 caracteres
                
                # Verificar que contenga elementos básicos de un dump PostgreSQL
                required_elements = [
                    'PostgreSQL database dump',
                    'CREATE DATABASE',
                    'pos_odata'
                ]
                
                return all(element in content for element in required_elements)
                
        except Exception as e:
            logger.error(f"Error verificando backup: {e}")
            return False

def main():
    """Función principal"""
    logger.info("Iniciando servicio de backup automático")
    
    backup_service = DatabaseBackup()
    
    # Crear backup
    success = backup_service.create_backup()
    
    if success:
        logger.info("Backup completado exitosamente")
        sys.exit(0)
    else:
        logger.error("Error en el proceso de backup")
        sys.exit(1)

if __name__ == '__main__':
    main()
