#!/usr/bin/env python3
"""
Script de Validación Final del Sistema POS O'data
================================================

Ejecuta una validación completa del sistema para verificar que todo
esté funcionando correctamente antes del despliegue.

Versión: 2.0.0
Autor: Sistema POS Odata Team
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
import sqlite3

# Agregar el directorio padre al path para imports
sys.path.append(str(Path(__file__).parent.parent))

class SystemValidator:
    """Validador completo del sistema POS"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            'tests_passed': 0,
            'tests_failed': 0,
            'warnings': 0,
            'details': []
        }
        self.server_process = None
        
    def log_result(self, test_name: str, status: str, details: str = "", warning: bool = False):
        """Registra el resultado de una prueba"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.results['details'].append(result)
        
        if status == 'PASS':
            self.results['tests_passed'] += 1
            print(f"✅ {test_name}: {status}")
        elif status == 'FAIL':
            self.results['tests_failed'] += 1
            print(f"❌ {test_name}: {status}")
            if details:
                print(f"   📝 {details}")
        elif status == 'WARNING' or warning:
            self.results['warnings'] += 1
            print(f"⚠️  {test_name}: {status}")
            if details:
                print(f"   📝 {details}")
    
    def check_python_version(self):
        """Verifica la versión de Python"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 11:
            self.log_result("Python Version", "PASS", f"Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.log_result("Python Version", "FAIL", f"Python {version.major}.{version.minor}.{version.micro} - Requerido: 3.11+")
    
    def check_dependencies(self):
        """Verifica que las dependencias estén instaladas"""
        required_packages = [
            'flask', 'flask_sqlalchemy', 'flask_jwt_extended', 
            'scikit-learn', 'numpy', 'redis', 'psycopg2'
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                self.log_result(f"Package {package}", "PASS")
            except ImportError:
                self.log_result(f"Package {package}", "FAIL", f"Paquete {package} no instalado")
    
    def check_file_structure(self):
        """Verifica la estructura de archivos del proyecto"""
        required_files = [
            'app/__init__.py',
            'app/core/config.py',
            'app/core/database.py',
            'app/models/user.py',
            'app/models/product.py',
            'app/api/v1/routes.py',
            'app/api/v2/routes.py',
            'requirements.txt',
            'run_server.py',
            'README.md'
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.log_result(f"File {file_path}", "PASS")
            else:
                self.log_result(f"File {file_path}", "FAIL", f"Archivo requerido no encontrado")
    
    def check_database_connection(self):
        """Verifica la conexión a la base de datos"""
        try:
            # Para SQLite de desarrollo
            db_path = self.project_root / 'instance' / 'pos_odata_dev.db'
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                conn.close()
                
                if len(tables) > 0:
                    self.log_result("Database Connection", "PASS", f"SQLite - {len(tables)} tablas encontradas")
                else:
                    self.log_result("Database Connection", "WARNING", "Base de datos vacía - ejecutar migraciones")
            else:
                self.log_result("Database Connection", "WARNING", "Base de datos no existe - se creará automáticamente")
                
        except Exception as e:
            self.log_result("Database Connection", "FAIL", f"Error conectando a la base de datos: {e}")
    
    def check_environment_config(self):
        """Verifica la configuración de entorno"""
        env_file = self.project_root / '.env'
        
        if not env_file.exists():
            self.log_result("Environment Config", "WARNING", "Archivo .env no encontrado - usando configuración por defecto")
            return
        
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                
                # Verificar variables críticas
                if 'SECRET_KEY=' in content and 'dev-secret-key' not in content:
                    self.log_result("Secret Key", "PASS", "SECRET_KEY configurado")
                else:
                    self.log_result("Secret Key", "FAIL", "SECRET_KEY no configurado o usando valor por defecto")
                
                if 'JWT_SECRET_KEY=' in content and 'jwt-secret-key' not in content:
                    self.log_result("JWT Secret Key", "PASS", "JWT_SECRET_KEY configurado")
                else:
                    self.log_result("JWT Secret Key", "FAIL", "JWT_SECRET_KEY no configurado o usando valor por defecto")
                    
        except Exception as e:
            self.log_result("Environment Config", "FAIL", f"Error leyendo .env: {e}")
    
    def start_test_server(self):
        """Inicia el servidor para pruebas"""
        try:
            # Cambiar al directorio del proyecto
            os.chdir(self.project_root)
            
            # Iniciar servidor en background
            self.server_process = subprocess.Popen(
                [sys.executable, 'run_server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, 'FLASK_ENV': 'development'}
            )
            
            # Esperar a que el servidor inicie
            time.sleep(5)
            
            # Verificar que el proceso esté ejecutándose
            if self.server_process.poll() is None:
                self.log_result("Test Server Start", "PASS", "Servidor iniciado en puerto 5000")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                self.log_result("Test Server Start", "FAIL", f"Error iniciando servidor: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.log_result("Test Server Start", "FAIL", f"Error iniciando servidor: {e}")
            return False
    
    def test_api_endpoints(self):
        """Prueba los endpoints principales de la API"""
        base_url = "http://localhost:5000"
        
        # Test endpoints básicos
        endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/api/v1/", "API v1 info"),
            ("/api/v2/", "API v2 info"),
            ("/api/v2/ai/health", "AI health check")
        ]
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    self.log_result(f"API {description}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_result(f"API {description}", "WARNING", f"Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"API {description}", "FAIL", f"Error: {e}")
    
    def test_ai_functionality(self):
        """Prueba las funcionalidades de IA"""
        base_url = "http://localhost:5000/api/v2"
        
        try:
            # Test AI stats
            response = requests.get(f"{base_url}/ai/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('service_status') == 'active':
                    self.log_result("AI Service", "PASS", f"Documentos: {data.get('total_documents', 0)}")
                else:
                    self.log_result("AI Service", "WARNING", "Servicio de IA inactivo")
            else:
                self.log_result("AI Service", "FAIL", f"Error en AI stats: {response.status_code}")
                
        except Exception as e:
            self.log_result("AI Service", "FAIL", f"Error probando IA: {e}")
    
    def stop_test_server(self):
        """Detiene el servidor de pruebas"""
        if self.server_process and self.server_process.poll() is None:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
                self.log_result("Test Server Stop", "PASS", "Servidor detenido correctamente")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.log_result("Test Server Stop", "WARNING", "Servidor forzado a terminar")
    
    def run_security_audit(self):
        """Ejecuta la auditoría de seguridad"""
        try:
            result = subprocess.run(
                [sys.executable, 'scripts/security_audit.py'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                self.log_result("Security Audit", "PASS", "Auditoría de seguridad completada")
            elif result.returncode == 1:
                self.log_result("Security Audit", "WARNING", "Auditoría con advertencias")
            else:
                self.log_result("Security Audit", "FAIL", "Problemas críticos de seguridad")
                
        except Exception as e:
            self.log_result("Security Audit", "FAIL", f"Error ejecutando auditoría: {e}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Genera el reporte final"""
        total_tests = self.results['tests_passed'] + self.results['tests_failed']
        success_rate = (self.results['tests_passed'] / total_tests * 100) if total_tests > 0 else 0
        
        # Determinar estado general
        if self.results['tests_failed'] == 0 and self.results['warnings'] <= 2:
            overall_status = "EXCELENTE"
            status_emoji = "🟢"
        elif self.results['tests_failed'] <= 2 and self.results['warnings'] <= 5:
            overall_status = "BUENO"
            status_emoji = "🟡"
        elif self.results['tests_failed'] <= 5:
            overall_status = "REGULAR"
            status_emoji = "🟠"
        else:
            overall_status = "CRÍTICO"
            status_emoji = "🔴"
        
        return {
            'overall_status': overall_status,
            'status_emoji': status_emoji,
            'success_rate': round(success_rate, 2),
            'total_tests': total_tests,
            'tests_passed': self.results['tests_passed'],
            'tests_failed': self.results['tests_failed'],
            'warnings': self.results['warnings'],
            'details': self.results['details']
        }
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Ejecuta la validación completa del sistema"""
        print("🔍 INICIANDO VALIDACIÓN COMPLETA DEL SISTEMA")
        print("=" * 60)
        
        try:
            # Validaciones básicas
            print("\n📋 VALIDACIONES BÁSICAS:")
            self.check_python_version()
            self.check_dependencies()
            self.check_file_structure()
            self.check_environment_config()
            self.check_database_connection()
            
            # Validaciones de seguridad
            print("\n🔒 VALIDACIONES DE SEGURIDAD:")
            self.run_security_audit()
            
            # Validaciones de funcionalidad
            print("\n🚀 VALIDACIONES DE FUNCIONALIDAD:")
            if self.start_test_server():
                time.sleep(2)  # Dar tiempo al servidor
                self.test_api_endpoints()
                self.test_ai_functionality()
                self.stop_test_server()
            else:
                self.log_result("API Tests", "FAIL", "No se pudo iniciar el servidor")
                self.log_result("AI Tests", "FAIL", "No se pudo iniciar el servidor")
            
            return self.generate_report()
            
        except Exception as e:
            self.log_result("System Validation", "FAIL", f"Error inesperado: {e}")
            return self.generate_report()

def print_validation_report(report: Dict[str, Any]):
    """Imprime el reporte de validación"""
    
    print("\n" + "=" * 70)
    print("🎯 REPORTE DE VALIDACIÓN FINAL DEL SISTEMA")
    print("=" * 70)
    
    print(f"\n📊 ESTADO GENERAL: {report['overall_status']} {report['status_emoji']}")
    print(f"📈 TASA DE ÉXITO: {report['success_rate']}%")
    
    print(f"\n📋 RESUMEN DE PRUEBAS:")
    print(f"   ✅ Pruebas exitosas: {report['tests_passed']}")
    print(f"   ❌ Pruebas fallidas: {report['tests_failed']}")
    print(f"   ⚠️  Advertencias: {report['warnings']}")
    print(f"   📊 Total de pruebas: {report['total_tests']}")
    
    # Mostrar detalles de pruebas fallidas
    failed_tests = [d for d in report['details'] if d['status'] == 'FAIL']
    if failed_tests:
        print(f"\n❌ PRUEBAS FALLIDAS:")
        for test in failed_tests:
            print(f"   • {test['test']}: {test['details']}")
    
    # Mostrar advertencias
    warnings = [d for d in report['details'] if d['status'] == 'WARNING']
    if warnings:
        print(f"\n⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"   • {warning['test']}: {warning['details']}")
    
    # Recomendaciones finales
    print(f"\n🎯 RECOMENDACIONES:")
    if report['overall_status'] == 'CRÍTICO':
        print("   🚨 URGENTE: Resolver problemas críticos antes del despliegue")
        print("   🔧 Revisar configuración y dependencias")
        print("   🔄 Ejecutar validación nuevamente después de correcciones")
    elif report['overall_status'] == 'REGULAR':
        print("   🔧 Resolver problemas identificados")
        print("   ⚠️  Revisar advertencias")
        print("   ✅ Sistema funcional pero necesita mejoras")
    elif report['overall_status'] == 'BUENO':
        print("   ✅ Sistema en buen estado")
        print("   🔍 Revisar advertencias menores")
        print("   🚀 Listo para despliegue con supervisión")
    else:
        print("   🎉 ¡Sistema completamente validado!")
        print("   🚀 Listo para despliegue en producción")
        print("   📊 Monitorear métricas post-despliegue")
    
    print("\n" + "=" * 70)

def main():
    """Función principal"""
    validator = SystemValidator()
    
    try:
        report = validator.run_full_validation()
        print_validation_report(report)
        
        # Guardar reporte
        report_file = validator.project_root / 'system_validation_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Reporte guardado en: {report_file}")
        
        # Código de salida basado en el estado
        if report['overall_status'] == 'CRÍTICO':
            sys.exit(2)
        elif report['overall_status'] in ['REGULAR', 'BUENO']:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Validación interrumpida por el usuario")
        validator.stop_test_server()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado durante la validación: {e}")
        validator.stop_test_server()
        sys.exit(2)

if __name__ == "__main__":
    main()
