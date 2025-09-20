#!/usr/bin/env python3
"""
Sistema de Backup Automático - Sistema POS O'Data
=================================================
Script de backup automático para producción
"""

import os
import sys
import subprocess
import shutil
import gzip
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackupAutomation:
    """Sistema de backup automático para el POS"""
    
    def __init__(self, backup_dir: str = "/backups"):
        self.backup_dir = backup_dir
        self.retention_days = 30  # Retener backups por 30 días
        self.max_backups = 50  # Máximo 50 backups
        
        # Crear directorio de backup si no existe
        os.makedirs(backup_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        logger.info(f"Backup automation iniciado - Directorio: {backup_dir}")
    
    def create_database_backup(self) -> Optional[str]:
        """
        Crear backup de la base de datos
        
        Returns:
            Optional[str]: Ruta del archivo de backup creado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Verificar tipo de base de datos
            database_url = os.environ.get('DATABASE_URL', 'sqlite:///pos_production.db')
            
            if database_url.startswith('postgresql://'):
                # Backup de PostgreSQL
                backup_file = f"{self.backup_dir}/postgres_backup_{timestamp}.sql"
                
                # Extraer información de conexión
                # Formato: postgresql://user:password@host:port/database
                import urllib.parse
                parsed = urllib.parse.urlparse(database_url)
                
                host = parsed.hostname or 'localhost'
                port = parsed.port or 5432
                database = parsed.path[1:]  # Remover el /
                username = parsed.username
                password = parsed.password
                
                # Crear backup con pg_dump
                env = os.environ.copy()
                env['PGPASSWORD'] = password
                
                cmd = [
                    'pg_dump',
                    '-h', host,
                    '-p', str(port),
                    '-U', username,
                    '-d', database,
                    '-f', backup_file
                ]
                
                result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"Backup de PostgreSQL creado: {backup_file}")
                    return backup_file
                else:
                    logger.error(f"Error creando backup de PostgreSQL: {result.stderr}")
                    return None
                    
            else:
                # Backup de SQLite
                db_file = database_url.replace('sqlite:///', '')
                if not os.path.exists(db_file):
                    logger.error(f"Archivo de base de datos no encontrado: {db_file}")
                    return None
                
                backup_file = f"{self.backup_dir}/sqlite_backup_{timestamp}.db"
                shutil.copy2(db_file, backup_file)
                
                logger.info(f"Backup de SQLite creado: {backup_file}")
                return backup_file
                
        except Exception as e:
            logger.error(f"Error creando backup de base de datos: {e}")
            return None
    
    def create_application_backup(self) -> Optional[str]:
        """
        Crear backup de la aplicación (código, configuraciones, etc.)
        
        Returns:
            Optional[str]: Ruta del archivo de backup creado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Archivos y directorios a incluir en el backup
            include_items = [
                'app/',
                'minimal_pos.py',
                'requirements.txt',
                'docker-compose.production.yml',
                'Dockerfile.minimal',
                'nginx/',
                'monitoring/',
                'scripts/',
                'logs/',
                'data/'
            ]
            
            # Crear archivo temporal
            temp_backup = f"{self.backup_dir}/app_backup_{timestamp}.tar"
            
            # Crear tar.gz
            cmd = ['tar', '-czf', temp_backup] + include_items
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Backup de aplicación creado: {temp_backup}")
                return temp_backup
            else:
                logger.error(f"Error creando backup de aplicación: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error creando backup de aplicación: {e}")
            return None
    
    def create_configuration_backup(self) -> Optional[str]:
        """
        Crear backup de configuraciones
        
        Returns:
            Optional[str]: Ruta del archivo de backup creado
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            config_data = {
                'timestamp': timestamp,
                'environment_variables': dict(os.environ),
                'docker_containers': self.get_docker_containers_info(),
                'system_info': self.get_system_info()
            }
            
            config_file = f"{self.backup_dir}/config_backup_{timestamp}.json"
            
            with open(config_file, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            logger.info(f"Backup de configuración creado: {config_file}")
            return config_file
            
        except Exception as e:
            logger.error(f"Error creando backup de configuración: {e}")
            return None
    
    def get_docker_containers_info(self) -> Dict:
        """Obtener información de contenedores Docker"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', 'json'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        containers.append(json.loads(line))
                return {'containers': containers}
            else:
                return {'error': result.stderr}
                
        except Exception as e:
            return {'error': str(e)}
    
    def get_system_info(self) -> Dict:
        """Obtener información del sistema"""
        try:
            import platform
            import psutil
            
            return {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_usage': psutil.disk_usage('/').percent
            }
        except Exception as e:
            return {'error': str(e)}
    
    def compress_backup(self, backup_file: str) -> Optional[str]:
        """
        Comprimir archivo de backup
        
        Args:
            backup_file: Ruta del archivo a comprimir
            
        Returns:
            Optional[str]: Ruta del archivo comprimido
        """
        try:
            compressed_file = f"{backup_file}.gz"
            
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Eliminar archivo original
            os.remove(backup_file)
            
            logger.info(f"Backup comprimido: {compressed_file}")
            return compressed_file
            
        except Exception as e:
            logger.error(f"Error comprimiendo backup: {e}")
            return None
    
    def cleanup_old_backups(self):
        """Limpiar backups antiguos"""
        try:
            # Obtener lista de archivos de backup
            backup_files = []
            for file in os.listdir(self.backup_dir):
                if file.endswith(('.sql', '.db', '.tar', '.gz')):
                    file_path = os.path.join(self.backup_dir, file)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    backup_files.append((file_path, file_time))
            
            # Ordenar por fecha (más recientes primero)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Eliminar backups antiguos
            removed_count = 0
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            for file_path, file_time in backup_files:
                if file_time < cutoff_date or len(backup_files) - removed_count > self.max_backups:
                    try:
                        os.remove(file_path)
                        removed_count += 1
                        logger.info(f"Backup antiguo eliminado: {file_path}")
                    except Exception as e:
                        logger.error(f"Error eliminando backup: {e}")
            
            if removed_count > 0:
                logger.info(f"Limpieza completada: {removed_count} backups eliminados")
            
        except Exception as e:
            logger.error(f"Error en limpieza de backups: {e}")
    
    def create_full_backup(self) -> Dict[str, str]:
        """
        Crear backup completo del sistema
        
        Returns:
            Dict[str, str]: Diccionario con las rutas de los backups creados
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backups = {}
        
        logger.info(f"Iniciando backup completo - {timestamp}")
        
        # 1. Backup de base de datos
        db_backup = self.create_database_backup()
        if db_backup:
            backups['database'] = db_backup
        
        # 2. Backup de aplicación
        app_backup = self.create_application_backup()
        if app_backup:
            backups['application'] = app_backup
        
        # 3. Backup de configuración
        config_backup = self.create_configuration_backup()
        if config_backup:
            backups['configuration'] = config_backup
        
        # 4. Comprimir backups
        for key, backup_file in backups.items():
            compressed = self.compress_backup(backup_file)
            if compressed:
                backups[key] = compressed
        
        # 5. Limpiar backups antiguos
        self.cleanup_old_backups()
        
        # 6. Crear índice de backup
        self.create_backup_index(backups, timestamp)
        
        logger.info(f"Backup completo finalizado - {timestamp}")
        return backups
    
    def create_backup_index(self, backups: Dict[str, str], timestamp: str):
        """Crear índice del backup"""
        try:
            index_file = f"{self.backup_dir}/backup_index_{timestamp}.json"
            
            index_data = {
                'timestamp': timestamp,
                'backups': backups,
                'total_size': sum(os.path.getsize(f) for f in backups.values() if os.path.exists(f)),
                'retention_days': self.retention_days,
                'max_backups': self.max_backups
            }
            
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
            
            logger.info(f"Índice de backup creado: {index_file}")
            
        except Exception as e:
            logger.error(f"Error creando índice de backup: {e}")
    
    def restore_backup(self, backup_file: str, backup_type: str = "database") -> bool:
        """
        Restaurar backup
        
        Args:
            backup_file: Ruta del archivo de backup
            backup_type: Tipo de backup (database, application, configuration)
            
        Returns:
            bool: True si la restauración fue exitosa
        """
        try:
            if backup_type == "database":
                return self.restore_database_backup(backup_file)
            elif backup_type == "application":
                return self.restore_application_backup(backup_file)
            elif backup_type == "configuration":
                return self.restore_configuration_backup(backup_file)
            else:
                logger.error(f"Tipo de backup no soportado: {backup_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error restaurando backup: {e}")
            return False
    
    def restore_database_backup(self, backup_file: str) -> bool:
        """Restaurar backup de base de datos"""
        try:
            database_url = os.environ.get('DATABASE_URL', 'sqlite:///pos_production.db')
            
            if database_url.startswith('postgresql://'):
                # Restaurar PostgreSQL
                import urllib.parse
                parsed = urllib.parse.urlparse(database_url)
                
                host = parsed.hostname or 'localhost'
                port = parsed.port or 5432
                database = parsed.path[1:]
                username = parsed.username
                password = parsed.password
                
                env = os.environ.copy()
                env['PGPASSWORD'] = password
                
                cmd = [
                    'psql',
                    '-h', host,
                    '-p', str(port),
                    '-U', username,
                    '-d', database,
                    '-f', backup_file
                ]
                
                result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"Backup de PostgreSQL restaurado: {backup_file}")
                    return True
                else:
                    logger.error(f"Error restaurando PostgreSQL: {result.stderr}")
                    return False
            else:
                # Restaurar SQLite
                db_file = database_url.replace('sqlite:///', '')
                shutil.copy2(backup_file, db_file)
                logger.info(f"Backup de SQLite restaurado: {backup_file}")
                return True
                
        except Exception as e:
            logger.error(f"Error restaurando backup de base de datos: {e}")
            return False
    
    def restore_application_backup(self, backup_file: str) -> bool:
        """Restaurar backup de aplicación"""
        try:
            # Extraer archivo tar.gz
            cmd = ['tar', '-xzf', backup_file, '-C', '/']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Backup de aplicación restaurado: {backup_file}")
                return True
            else:
                logger.error(f"Error restaurando aplicación: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error restaurando backup de aplicación: {e}")
            return False
    
    def restore_configuration_backup(self, backup_file: str) -> bool:
        """Restaurar backup de configuración"""
        try:
            with open(backup_file, 'r') as f:
                config_data = json.load(f)
            
            logger.info(f"Backup de configuración restaurado: {backup_file}")
            logger.info(f"Configuración: {json.dumps(config_data, indent=2)}")
            return True
            
        except Exception as e:
            logger.error(f"Error restaurando backup de configuración: {e}")
            return False

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de Backup Automático - POS O\'Data')
    parser.add_argument('--backup-dir', default='/backups', help='Directorio de backups')
    parser.add_argument('--create', action='store_true', help='Crear backup completo')
    parser.add_argument('--restore', help='Restaurar backup específico')
    parser.add_argument('--type', choices=['database', 'application', 'configuration'], 
                       default='database', help='Tipo de backup a restaurar')
    parser.add_argument('--cleanup', action='store_true', help='Limpiar backups antiguos')
    
    args = parser.parse_args()
    
    # Crear instancia del sistema de backup
    backup_system = BackupAutomation(args.backup_dir)
    
    if args.create:
        # Crear backup completo
        backups = backup_system.create_full_backup()
        print(f"Backup completo creado:")
        for key, path in backups.items():
            print(f"  {key}: {path}")
    
    elif args.restore:
        # Restaurar backup
        success = backup_system.restore_backup(args.restore, args.type)
        if success:
            print(f"Backup restaurado exitosamente: {args.restore}")
        else:
            print(f"Error restaurando backup: {args.restore}")
            sys.exit(1)
    
    elif args.cleanup:
        # Limpiar backups antiguos
        backup_system.cleanup_old_backups()
        print("Limpieza de backups completada")
    
    else:
        print("Use --create, --restore, o --cleanup")

if __name__ == "__main__":
    main()
