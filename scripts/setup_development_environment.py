#!/usr/bin/env python3
"""
Script de Configuración del Entorno de Desarrollo - O'Data v2.0.0
================================================================

Este script configura automáticamente el entorno de desarrollo completo:
- Verifica versiones de Python y dependencias
- Instala dependencias faltantes
- Configura base de datos PostgreSQL
- Configura Redis
- Ejecuta migraciones
- Valida configuración

Autor: Sistema POS Odata
Versión: 2.0.0
"""

import os
import sys
import subprocess
import platform
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class DevelopmentEnvironmentSetup:
    """Configurador del entorno de desarrollo"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.requirements_file = self.project_root / "requirements.txt"
        self.requirements_dev_file = self.project_root / "requirements-dev.txt"
        self.env_file = self.project_root / ".env"
        self.env_example_file = self.project_root / "env.example"
        
        # Configuración por defecto
        self.config = {
            'python_version': '3.13',
            'postgres_port': 5432,
            'redis_port': 6379,
            'app_port': 8000,
            'frontend_port': 3000
        }
        
        self.errors = []
        self.warnings = []
        self.success = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log con timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
        if level == "ERROR":
            self.errors.append(message)
        elif level == "WARNING":
            self.warnings.append(message)
        elif level == "SUCCESS":
            self.success.append(message)
    
    def check_python_version(self) -> bool:
        """Verificar versión de Python"""
        self.log("Verificando versión de Python...")
        
        version = sys.version_info
        required_version = tuple(map(int, self.config['python_version'].split('.')))
        
        if version < required_version:
            self.log(f"❌ Python {version.major}.{version.minor}.{version.micro} detectado", "ERROR")
            self.log(f"   Se requiere Python {self.config['python_version']}+", "ERROR")
            self.log("   Actualiza Python desde: https://www.python.org/downloads/", "ERROR")
            return False
        
        self.log(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible", "SUCCESS")
        return True
    
    def check_system_requirements(self) -> bool:
        """Verificar requisitos del sistema"""
        self.log("Verificando requisitos del sistema...")
        
        # Verificar Docker
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log("✅ Docker detectado", "SUCCESS")
            else:
                self.log("❌ Docker no disponible", "ERROR")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("❌ Docker no encontrado", "ERROR")
            self.log("   Instala Docker desde: https://docs.docker.com/get-docker/", "ERROR")
            return False
        
        # Verificar Docker Compose
        try:
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log("✅ Docker Compose detectado", "SUCCESS")
            else:
                self.log("❌ Docker Compose no disponible", "ERROR")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log("❌ Docker Compose no encontrado", "ERROR")
            return False
        
        return True
    
    def install_python_dependencies(self) -> bool:
        """Instalar dependencias de Python"""
        self.log("Instalando dependencias de Python...")
        
        # Actualizar pip
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         check=True, capture_output=True)
            self.log("✅ pip actualizado", "SUCCESS")
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Error actualizando pip: {e}", "ERROR")
            return False
        
        # Instalar dependencias de producción
        if self.requirements_file.exists():
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(self.requirements_file)], 
                             check=True, capture_output=True)
                self.log("✅ Dependencias de producción instaladas", "SUCCESS")
            except subprocess.CalledProcessError as e:
                self.log(f"❌ Error instalando dependencias de producción: {e}", "ERROR")
                return False
        
        # Instalar dependencias de desarrollo
        if self.requirements_dev_file.exists():
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(self.requirements_dev_file)], 
                             check=True, capture_output=True)
                self.log("✅ Dependencias de desarrollo instaladas", "SUCCESS")
            except subprocess.CalledProcessError as e:
                self.log(f"❌ Error instalando dependencias de desarrollo: {e}", "ERROR")
                return False
        
        return True
    
    def create_env_file(self) -> bool:
        """Crear archivo .env desde env.example"""
        self.log("Configurando variables de entorno...")
        
        if not self.env_example_file.exists():
            self.log("❌ Archivo env.example no encontrado", "ERROR")
            return False
        
        if self.env_file.exists():
            self.log("⚠️ Archivo .env ya existe, respaldando...", "WARNING")
            backup_file = self.project_root / ".env.backup"
            self.env_file.rename(backup_file)
            self.log(f"✅ Backup creado: {backup_file}", "SUCCESS")
        
        # Copiar env.example a .env
        try:
            with open(self.env_example_file, 'r', encoding='utf-8') as f:
                env_content = f.read()
            
            # Personalizar configuración
            env_content = env_content.replace('DATABASE_URL=sqlite:///pos_odata_dev.db', 
                                           f'DATABASE_URL=postgresql://postgres:postgres@localhost:{self.config["postgres_port"]}/pos_odata_dev')
            env_content = env_content.replace('REDIS_URL=redis://localhost:6379/0',
                                           f'REDIS_URL=redis://localhost:{self.config["redis_port"]}/0')
            env_content = env_content.replace('SERVER_PORT=8000',
                                           f'SERVER_PORT={self.config["app_port"]}')
            
            with open(self.env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            self.log("✅ Archivo .env creado y configurado", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ Error creando archivo .env: {e}", "ERROR")
            return False
    
    def start_docker_services(self) -> bool:
        """Iniciar servicios Docker"""
        self.log("Iniciando servicios Docker...")
        
        try:
            # Detener servicios existentes
            subprocess.run(['docker-compose', 'down'], 
                         cwd=self.project_root, check=True, capture_output=True)
            self.log("✅ Servicios Docker detenidos", "SUCCESS")
            
            # Iniciar servicios
            subprocess.run(['docker-compose', 'up', '-d'], 
                         cwd=self.project_root, check=True, capture_output=True)
            self.log("✅ Servicios Docker iniciados", "SUCCESS")
            
            # Esperar a que los servicios estén listos
            self.log("Esperando a que los servicios estén listos...")
            time.sleep(30)
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Error iniciando servicios Docker: {e}", "ERROR")
            return False
    
    def run_database_migrations(self) -> bool:
        """Ejecutar migraciones de base de datos"""
        self.log("Ejecutando migraciones de base de datos...")
        
        try:
            # Verificar que la base de datos esté lista
            time.sleep(10)
            
            # Ejecutar migraciones
            subprocess.run([sys.executable, '-m', 'flask', 'db', 'upgrade'], 
                         cwd=self.project_root, check=True, capture_output=True)
            self.log("✅ Migraciones ejecutadas", "SUCCESS")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Error ejecutando migraciones: {e}", "ERROR")
            return False
    
    def validate_installation(self) -> bool:
        """Validar la instalación"""
        self.log("Validando instalación...")
        
        # Verificar que los servicios estén corriendo
        try:
            import requests
            response = requests.get(f"http://localhost:{self.config['app_port']}/health", timeout=10)
            if response.status_code == 200:
                self.log("✅ Backend respondiendo correctamente", "SUCCESS")
            else:
                self.log(f"❌ Backend respondió con código: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Backend no responde: {e}", "ERROR")
            return False
        
        # Verificar base de datos
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                port=self.config['postgres_port'],
                database="pos_odata_dev",
                user="postgres",
                password="postgres"
            )
            conn.close()
            self.log("✅ Base de datos PostgreSQL accesible", "SUCCESS")
        except Exception as e:
            self.log(f"❌ Error conectando a PostgreSQL: {e}", "ERROR")
            return False
        
        # Verificar Redis
        try:
            import redis
            r = redis.Redis(host='localhost', port=self.config['redis_port'], db=0)
            r.ping()
            self.log("✅ Redis accesible", "SUCCESS")
        except Exception as e:
            self.log(f"❌ Error conectando a Redis: {e}", "ERROR")
            return False
        
        return True
    
    def run_tests(self) -> bool:
        """Ejecutar tests básicos"""
        self.log("Ejecutando tests básicos...")
        
        try:
            # Tests unitarios básicos
            result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/backend/test_unit_backend.py', '-v'], 
                                 cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Tests unitarios pasaron", "SUCCESS")
            else:
                self.log(f"⚠️ Tests unitarios fallaron: {result.stdout}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error ejecutando tests: {e}", "ERROR")
            return False
    
    def generate_report(self):
        """Generar reporte de instalación"""
        self.log("Generando reporte de instalación...")
        
        report = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'system': platform.system(),
            'architecture': platform.architecture()[0],
            'success_count': len(self.success),
            'warning_count': len(self.warnings),
            'error_count': len(self.errors),
            'success': self.success,
            'warnings': self.warnings,
            'errors': self.errors
        }
        
        report_file = self.project_root / "development_setup_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"✅ Reporte generado: {report_file}", "SUCCESS")
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("RESUMEN DE INSTALACIÓN")
        print("="*60)
        print(f"✅ Exitosos: {len(self.success)}")
        print(f"⚠️ Advertencias: {len(self.warnings)}")
        print(f"❌ Errores: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ ERRORES CRÍTICOS:")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print("\n⚠️ ADVERTENCIAS:")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if self.success:
            print("\n✅ INSTALACIÓN EXITOSA:")
            for success in self.success:
                print(f"   - {success}")
        
        print("\n" + "="*60)
    
    def run(self) -> bool:
        """Ejecutar configuración completa"""
        self.log("🚀 Iniciando configuración del entorno de desarrollo...")
        
        steps = [
            ("Verificar versión de Python", self.check_python_version),
            ("Verificar requisitos del sistema", self.check_system_requirements),
            ("Instalar dependencias de Python", self.install_python_dependencies),
            ("Configurar variables de entorno", self.create_env_file),
            ("Iniciar servicios Docker", self.start_docker_services),
            ("Ejecutar migraciones", self.run_database_migrations),
            ("Validar instalación", self.validate_installation),
            ("Ejecutar tests básicos", self.run_tests)
        ]
        
        for step_name, step_func in steps:
            self.log(f"\n--- {step_name} ---")
            if not step_func():
                self.log(f"❌ Falló: {step_name}", "ERROR")
                return False
            self.log(f"✅ Completado: {step_name}", "SUCCESS")
        
        self.generate_report()
        return len(self.errors) == 0

def main():
    """Función principal"""
    print("="*60)
    print("CONFIGURADOR DEL ENTORNO DE DESARROLLO - O'DATA v2.0.0")
    print("="*60)
    
    setup = DevelopmentEnvironmentSetup()
    
    try:
        success = setup.run()
        if success:
            print("\n🎉 ¡Entorno de desarrollo configurado exitosamente!")
            print("📚 Próximos pasos:")
            print("   1. Ejecuta: python -m pytest tests/ -v --cov=app")
            print("   2. Inicia el servidor: python run_server.py")
            print("   3. Abre el frontend: http://localhost:3000")
        else:
            print("\n❌ La configuración falló. Revisa los errores arriba.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Configuración interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
