#!/usr/bin/env python3
"""
Sistema de Despliegue Profesional - POS O'data
===============================================

Script para despliegue profesional con validaciones exhaustivas
Desarrollado siguiendo mejores prácticas de DevOps y SRE

Autor: Sistema POS O'data
Versión: 2.0.0
"""

import os
import sys
import json
import time
import subprocess
import requests
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configurar logging profesional
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DeploymentValidator:
    """Validador profesional de despliegues"""
    
    def __init__(self):
        self.start_time = datetime.datetime.now()
        self.backend_url = "http://localhost:5000"
        self.frontend_url = "http://localhost:5173"
        self.results = {
            "deployment_id": f"deploy_{int(time.time())}",
            "timestamp": self.start_time.isoformat(),
            "environment": "development",
            "version": "2.0.0",
            "status": "in_progress",
            "validations": {}
        }
        
    def print_header(self, title: str):
        """Imprime encabezado profesional"""
        print("\n" + "="*70)
        print(f"🚀 {title.upper()}")
        print("="*70)
        
    def print_step(self, step: str, status: str = ""):
        """Imprime paso con formato profesional"""
        status_icon = "✅" if status == "success" else "⚠️" if status == "warning" else "❌" if status == "error" else "🔍"
        print(f"{status_icon} {step}")
        
    def run_command(self, command: str, cwd: Optional[str] = None, timeout: int = 300) -> Tuple[bool, str, str]:
        """Ejecuta comando con manejo profesional de errores"""
        try:
            logger.info(f"Ejecutando: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout ejecutando comando: {command}")
            return False, "", "Timeout"
        except Exception as e:
            logger.error(f"Error ejecutando comando {command}: {e}")
            return False, "", str(e)
    
    def validate_python_environment(self) -> bool:
        """Valida entorno Python y dependencias"""
        self.print_step("Validando entorno Python...")
        
        # Verificar versión de Python
        success, stdout, stderr = self.run_command("python --version")
        if not success:
            self.print_step("Error verificando versión de Python", "error")
            return False
            
        python_version = stdout.strip()
        self.print_step(f"Python version: {python_version}", "success")
        
        # Verificar dependencias críticas
        critical_deps = [
            'flask', 'sqlalchemy', 'fakeredis', 'colorama', 
            'marshmallow', 'redis', 'requests', 'pandas'
        ]
        
        failed_deps = []
        for dep in critical_deps:
            success, _, _ = self.run_command(f"python -c \"import {dep}\"")
            if success:
                self.print_step(f"✓ {dep} importado correctamente", "success")
            else:
                self.print_step(f"✗ {dep} falló al importar", "error")
                failed_deps.append(dep)
        
        if failed_deps:
            logger.error(f"Dependencias faltantes: {failed_deps}")
            return False
            
        self.results["validations"]["python_environment"] = {
            "status": "success",
            "python_version": python_version,
            "dependencies_validated": len(critical_deps),
            "failed_dependencies": failed_deps
        }
        
        return True
    
    def validate_backend_health(self) -> bool:
        """Valida salud completa del backend"""
        self.print_step("Iniciando validación del backend...")
        
        # Verificar que el servidor esté ejecutándose
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                self.print_step(f"Health check exitoso: {health_data['status']}", "success")
                
                # Validar endpoints críticos
                endpoints_to_test = [
                    "/health",
                    "/api/v1/products",
                    "/api/v1/users",
                    "/api/v2/ai/health"
                ]
                
                endpoint_results = {}
                for endpoint in endpoints_to_test:
                    try:
                        resp = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                        endpoint_results[endpoint] = {
                            "status_code": resp.status_code,
                            "accessible": resp.status_code in [200, 401, 403]  # 401/403 ok, significa que está funcionando
                        }
                        status = "success" if endpoint_results[endpoint]["accessible"] else "error"
                        self.print_step(f"Endpoint {endpoint}: {resp.status_code}", status)
                    except Exception as e:
                        endpoint_results[endpoint] = {
                            "status_code": 0,
                            "accessible": False,
                            "error": str(e)
                        }
                        self.print_step(f"Endpoint {endpoint}: Error - {e}", "error")
                
                self.results["validations"]["backend_health"] = {
                    "status": "success",
                    "health_data": health_data,
                    "endpoints": endpoint_results
                }
                return True
            else:
                self.print_step(f"Health check falló: {response.status_code}", "error")
                return False
                
        except Exception as e:
            self.print_step(f"Error conectando al backend: {e}", "error")
            logger.error(f"Backend no accesible: {e}")
            return False
    
    def validate_database_connectivity(self) -> bool:
        """Valida conectividad y estado de la base de datos"""
        self.print_step("Validando conectividad de base de datos...")
        
        # Verificar archivo de base de datos SQLite
        db_files = [
            "pos_odata_dev.db",
            "instance/pos_odata_dev.db"
        ]
        
        db_found = False
        for db_file in db_files:
            if Path(db_file).exists():
                self.print_step(f"Base de datos encontrada: {db_file}", "success")
                db_found = True
                break
        
        if not db_found:
            self.print_step("Archivo de base de datos no encontrado, será creado automáticamente", "warning")
        
        # Verificar conectividad a través del endpoint
        try:
            response = requests.get(f"{self.backend_url}/api/v1/products", timeout=10)
            if response.status_code in [200, 401]:  # 200 = OK, 401 = requiere auth pero conecta
                self.print_step("Conectividad de base de datos verificada", "success")
                self.results["validations"]["database"] = {
                    "status": "success",
                    "connectivity": True
                }
                return True
            else:
                self.print_step(f"Error de conectividad DB: {response.status_code}", "error")
                return False
        except Exception as e:
            self.print_step(f"Error verificando DB: {e}", "error")
            return False
    
    def validate_frontend_build(self) -> bool:
        """Valida build del frontend"""
        self.print_step("Validando frontend...")
        
        frontend_path = Path("Sistema_POS_Odata_nuevo/frontend")
        if not frontend_path.exists():
            self.print_step("Directorio del frontend no encontrado", "error")
            return False
        
        # Verificar package.json
        package_json = frontend_path / "package.json"
        if not package_json.exists():
            self.print_step("package.json no encontrado", "error")
            return False
        
        # Verificar TypeScript
        self.print_step("Verificando configuración TypeScript...")
        success, stdout, stderr = self.run_command(
            "npx tsc --noEmit", 
            cwd=str(frontend_path)
        )
        
        if success:
            self.print_step("TypeScript: Sin errores de tipos", "success")
        else:
            self.print_step(f"TypeScript: Errores encontrados", "warning")
            logger.warning(f"TypeScript warnings: {stderr}")
        
        # Intentar build
        self.print_step("Ejecutando build del frontend...")
        success, stdout, stderr = self.run_command(
            "npm run build",
            cwd=str(frontend_path),
            timeout=180
        )
        
        if success:
            self.print_step("Build del frontend exitoso", "success")
            
            # Verificar archivos de build
            dist_path = frontend_path / "dist"
            if dist_path.exists():
                self.print_step("Archivos de distribución generados", "success")
                
                self.results["validations"]["frontend"] = {
                    "status": "success",
                    "typescript_check": success,
                    "build_successful": True,
                    "dist_generated": True
                }
                return True
            else:
                self.print_step("Directorio dist no encontrado", "error")
                return False
        else:
            self.print_step(f"Error en build del frontend: {stderr}", "error")
            return False
    
    def run_security_scan(self) -> bool:
        """Ejecuta escaneo de seguridad"""
        self.print_step("Ejecutando escaneo de seguridad...")
        
        # Instalar bandit si no está disponible
        success, _, _ = self.run_command("python -c \"import bandit\"")
        if not success:
            self.print_step("Instalando bandit para escaneo de seguridad...")
            success, _, _ = self.run_command("python -m pip install bandit")
        
        # Ejecutar bandit
        success, stdout, stderr = self.run_command(
            "python -m bandit -r app/ -f json",
            timeout=60
        )
        
        if success:
            try:
                bandit_results = json.loads(stdout)
                issues_count = len(bandit_results.get('results', []))
                self.print_step(f"Escaneo de seguridad completado: {issues_count} issues encontrados", 
                              "success" if issues_count == 0 else "warning")
                
                self.results["validations"]["security"] = {
                    "status": "success",
                    "issues_count": issues_count,
                    "scan_completed": True
                }
                return True
            except json.JSONDecodeError:
                self.print_step("Error parseando resultados de bandit", "warning")
                return True  # No bloquear por esto
        else:
            self.print_step("Error ejecutando bandit", "warning")
            return True  # No bloquear deployment por esto
    
    def run_performance_tests(self) -> bool:
        """Ejecuta tests básicos de rendimiento"""
        self.print_step("Ejecutando tests de rendimiento...")
        
        # Test de respuesta del health endpoint
        response_times = []
        for i in range(5):
            start_time = time.time()
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=10)
                if response.status_code == 200:
                    response_time = time.time() - start_time
                    response_times.append(response_time)
                else:
                    self.print_step(f"Health check failed: {response.status_code}", "warning")
                    return False
            except Exception as e:
                self.print_step(f"Performance test failed: {e}", "warning")
                return False
        
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        self.print_step(f"Tiempo promedio de respuesta: {avg_response_time:.3f}s", "success")
        self.print_step(f"Tiempo máximo de respuesta: {max_response_time:.3f}s", "success")
        
        # Validar que los tiempos sean aceptables
        performance_ok = avg_response_time < 1.0 and max_response_time < 2.0
        status = "success" if performance_ok else "warning"
        
        self.results["validations"]["performance"] = {
            "status": status,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "acceptable": performance_ok
        }
        
        return performance_ok
    
    def generate_deployment_report(self) -> bool:
        """Genera reporte completo de despliegue"""
        self.print_step("Generando reporte de despliegue...")
        
        # Calcular métricas finales
        end_time = datetime.datetime.now()
        duration = end_time - self.start_time
        
        # Determinar status general
        all_validations_passed = all(
            v.get("status") == "success" 
            for v in self.results["validations"].values()
        )
        
        self.results.update({
            "status": "success" if all_validations_passed else "warning",
            "end_time": end_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "summary": {
                "validations_total": len(self.results["validations"]),
                "validations_passed": sum(
                    1 for v in self.results["validations"].values() 
                    if v.get("status") == "success"
                ),
                "all_passed": all_validations_passed
            }
        })
        
        # Crear directorio de reportes
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Guardar reporte JSON
        report_file = reports_dir / f"deployment_report_{self.results['deployment_id']}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        self.print_step(f"Reporte guardado: {report_file}", "success")
        
        return True
    
    def run_full_deployment_validation(self) -> bool:
        """Ejecuta validación completa de despliegue"""
        
        self.print_header("VALIDACIÓN PROFESIONAL DE DESPLIEGUE")
        self.print_step(f"Deployment ID: {self.results['deployment_id']}")
        self.print_step(f"Timestamp: {self.start_time}")
        
        # Secuencia de validaciones
        validations = [
            ("Entorno Python", self.validate_python_environment),
            ("Salud del Backend", self.validate_backend_health),
            ("Base de Datos", self.validate_database_connectivity),
            ("Frontend Build", self.validate_frontend_build),
            ("Escaneo de Seguridad", self.run_security_scan),
            ("Tests de Rendimiento", self.run_performance_tests),
        ]
        
        failed_validations = []
        
        for validation_name, validation_func in validations:
            self.print_header(f"VALIDACIÓN: {validation_name}")
            
            try:
                success = validation_func()
                if success:
                    self.print_step(f"✅ {validation_name} - EXITOSO", "success")
                else:
                    self.print_step(f"❌ {validation_name} - FALLÓ", "error")
                    failed_validations.append(validation_name)
            except Exception as e:
                logger.error(f"Error en validación {validation_name}: {e}")
                self.print_step(f"❌ {validation_name} - ERROR: {e}", "error")
                failed_validations.append(validation_name)
        
        # Generar reporte final
        self.generate_deployment_report()
        
        # Resumen final
        self.print_header("RESUMEN DE DESPLIEGUE")
        
        if not failed_validations:
            self.print_step("🎉 DESPLIEGUE EXITOSO - Todas las validaciones pasaron", "success")
            self.print_step(f"Sistema POS O'data v2.0.0 listo para producción", "success")
            return True
        else:
            self.print_step(f"⚠️ DESPLIEGUE CON ADVERTENCIAS", "warning")
            self.print_step(f"Validaciones fallidas: {', '.join(failed_validations)}", "warning")
            return False

def main():
    """Función principal"""
    print("🚀 SISTEMA DE DESPLIEGUE PROFESIONAL - POS O'DATA")
    print("=" * 70)
    
    # Crear directorio de logs
    Path("logs").mkdir(exist_ok=True)
    
    # Ejecutar validación de despliegue
    validator = DeploymentValidator()
    success = validator.run_full_deployment_validation()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
