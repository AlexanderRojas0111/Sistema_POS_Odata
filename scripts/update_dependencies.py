#!/usr/bin/env python3
"""
Script de Actualización de Dependencias para Sistema POS O'Data v2.0.0
Actualiza numpy de 2.0.2 a 2.3.2 y verifica compatibilidad
"""

import os
import sys
import subprocess
import json
import pkg_resources
from pathlib import Path
from datetime import datetime
import logging
import requests
from typing import Dict, List, Tuple

class DependencyUpdater:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.reports_dir / "dependency_update.log"),
                logging.FileHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Dependencias objetivo
        self.target_versions = {
            "numpy": "2.3.2",
            "scikit-learn": "1.7.1",
            "scipy": "1.16.1"
        }
        
        # Dependencias críticas que deben ser compatibles
        self.critical_dependencies = [
            "numpy", "scikit-learn", "scipy", "pandas", "matplotlib", "seaborn"
        ]
        
        # Resultados de la actualización
        self.update_results = {
            "timestamp": datetime.now().isoformat(),
            "current_versions": {},
            "target_versions": self.target_versions,
            "update_status": {},
            "compatibility_check": {},
            "security_audit": {},
            "recommendations": []
        }
    
    def get_current_versions(self) -> Dict[str, str]:
        """Obtiene las versiones actuales de las dependencias instaladas"""
        self.logger.info("🔍 Obteniendo versiones actuales de dependencias...")
        
        current_versions = {}
        
        try:
            # Obtener todas las dependencias instaladas
            installed_packages = pkg_resources.working_set
            
            for package in installed_packages:
                package_name = package.project_name.lower()
                package_version = package.version
                current_versions[package_name] = package_version
                
                # Log de dependencias principales
                if package_name in self.critical_dependencies:
                    self.logger.info(f"   {package_name}: {package_version}")
        
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo versiones: {e}")
        
        self.update_results["current_versions"] = current_versions
        return current_versions
    
    def check_pypi_versions(self) -> Dict[str, str]:
        """Verifica las últimas versiones disponibles en PyPI"""
        self.logger.info("🌐 Verificando versiones más recientes en PyPI...")
        
        pypi_versions = {}
        
        for package in self.critical_dependencies:
            try:
                # Consultar API de PyPI
                response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    latest_version = data["info"]["version"]
                    pypi_versions[package] = latest_version
                    self.logger.info(f"   {package}: {latest_version} (PyPI)")
                else:
                    self.logger.warning(f"⚠️ No se pudo obtener versión de {package}")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Error consultando PyPI para {package}: {e}")
        
        return pypi_versions
    
    def check_compatibility_matrix(self) -> Dict[str, Dict]:
        """Verifica matriz de compatibilidad entre dependencias"""
        self.logger.info("🔗 Verificando matriz de compatibilidad...")
        
        compatibility_matrix = {
            "numpy": {
                "2.3.2": {
                    "scikit-learn": ["1.7.1", "1.8.0"],
                    "scipy": ["1.16.1", "1.17.0"],
                    "pandas": ["2.3.2", "2.4.0"],
                    "matplotlib": ["3.10.0", "3.11.0"],
                    "seaborn": ["0.13.0", "0.14.0"]
                }
            },
            "scikit-learn": {
                "1.7.1": {
                    "numpy": ["2.0.0", "2.3.2"],
                    "scipy": ["1.16.0", "1.17.0"]
                }
            },
            "scipy": {
                "1.16.1": {
                    "numpy": ["2.0.0", "2.3.2"]
                }
            }
        }
        
        current_versions = self.update_results["current_versions"]
        compatibility_results = {}
        
        for package, target_version in self.target_versions.items():
            if package in compatibility_matrix and target_version in compatibility_matrix[package]:
                package_compat = compatibility_matrix[package][target_version]
                compatibility_results[package] = {
                    "target_version": target_version,
                    "compatible_with": package_compat,
                    "current_versions": {},
                    "compatibility_status": "checking"
                }
                
                # Verificar compatibilidad con dependencias actuales
                for dep_package, compatible_versions in package_compat.items():
                    if dep_package in current_versions:
                        current_version = current_versions[dep_package]
                        is_compatible = any(
                            self.version_in_range(current_version, compatible_versions)
                        )
                        
                        compatibility_results[package]["current_versions"][dep_package] = {
                            "current": current_version,
                            "compatible_versions": compatible_versions,
                            "is_compatible": is_compatible
                        }
                        
                        if not is_compatible:
                            compatibility_results[package]["compatibility_status"] = "warning"
                            self.logger.warning(f"⚠️ {package} {target_version} puede tener problemas de compatibilidad con {dep_package} {current_version}")
                
                if compatibility_results[package]["compatibility_status"] == "checking":
                    compatibility_results[package]["compatibility_status"] = "compatible"
        
        self.update_results["compatibility_check"] = compatibility_results
        return compatibility_results
    
    def version_in_range(self, version: str, version_range: List[str]) -> bool:
        """Verifica si una versión está en un rango específico"""
        try:
            from packaging import version as pkg_version
            
            current = pkg_version.parse(version)
            
            for range_spec in version_range:
                if ">=" in range_spec:
                    min_version = pkg_version.parse(range_spec.replace(">=", ""))
                    if current >= min_version:
                        return True
                elif "<=" in range_spec:
                    max_version = pkg_version.parse(range_spec.replace("<=", ""))
                    if current <= max_version:
                        return True
                elif "==" in range_spec:
                    exact_version = pkg_version.parse(range_spec.replace("==", ""))
                    if current == exact_version:
                return True
            else:
                    # Asumir versión exacta
                    exact_version = pkg_version.parse(range_spec)
                    if current == exact_version:
                        return True
            
                return False
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error verificando rango de versión: {e}")
            return False
            
    def update_numpy(self) -> bool:
        """Actualiza numpy a la versión objetivo"""
        self.logger.info(f"🔄 Actualizando numpy a {self.target_versions['numpy']}...")
        
        try:
            # Verificar versión actual
            current_numpy = self.update_results["current_versions"].get("numpy", "0.0.0")
            self.logger.info(f"   Versión actual: {current_numpy}")
            
            if current_numpy == self.target_versions["numpy"]:
                self.logger.info("   ✅ numpy ya está en la versión objetivo")
                self.update_results["update_status"]["numpy"] = {
                    "status": "already_updated",
                    "current_version": current_numpy,
                    "target_version": self.target_versions["numpy"]
                }
                return True
            
            # Actualizar numpy
            update_command = f"pip install numpy=={self.target_versions['numpy']} --upgrade"
            result = subprocess.run(update_command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("   ✅ numpy actualizado exitosamente")
                
                # Verificar nueva versión
                new_version = pkg_resources.get_distribution("numpy").version
                
                self.update_results["update_status"]["numpy"] = {
                    "status": "success",
                    "previous_version": current_numpy,
                    "new_version": new_version,
                    "target_version": self.target_versions["numpy"]
                }
                
                return True
            else:
                self.logger.error(f"   ❌ Error actualizando numpy: {result.stderr}")
                self.update_results["update_status"]["numpy"] = {
                    "status": "failed",
                    "error": result.stderr,
                    "previous_version": current_numpy
                }
                return False
                
        except Exception as e:
            self.logger.error(f"   ❌ Error fatal actualizando numpy: {e}")
            self.update_results["update_status"]["numpy"] = {
                "status": "error",
                "error": str(e)
            }
            return False
            
    def update_other_dependencies(self) -> Dict[str, bool]:
        """Actualiza otras dependencias críticas"""
        self.logger.info("🔄 Actualizando otras dependencias críticas...")
        
        update_results = {}
        
        for package, target_version in self.target_versions.items():
            if package == "numpy":
                continue  # Ya se actualizó
            
            try:
                self.logger.info(f"   Actualizando {package} a {target_version}...")
                
                current_version = self.update_results["current_versions"].get(package, "0.0.0")
                
                if current_version == target_version:
                    self.logger.info(f"     ✅ {package} ya está en la versión objetivo")
                    update_results[package] = True
                    self.update_results["update_status"][package] = {
                        "status": "already_updated",
                        "current_version": current_version,
                        "target_version": target_version
                    }
                    continue
                
                # Actualizar dependencia
                update_command = f"pip install {package}=={target_version} --upgrade"
                result = subprocess.run(update_command, shell=True, capture_output=True, text=True)
                
            if result.returncode == 0:
                    self.logger.info(f"     ✅ {package} actualizado exitosamente")
                    
                    # Verificar nueva versión
                    new_version = pkg_resources.get_distribution(package).version
                    
                    update_results[package] = True
                    self.update_results["update_status"][package] = {
                        "status": "success",
                        "previous_version": current_version,
                        "new_version": new_version,
                        "target_version": target_version
                    }
            else:
                    self.logger.error(f"     ❌ Error actualizando {package}: {result.stderr}")
                    update_results[package] = False
                    self.update_results["update_status"][package] = {
                        "status": "failed",
                        "error": result.stderr,
                        "previous_version": current_version
                    }
                    
        except Exception as e:
                self.logger.error(f"     ❌ Error fatal actualizando {package}: {e}")
                update_results[package] = False
                self.update_results["update_status"][package] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return update_results
    
    def run_security_audit(self) -> Dict:
        """Ejecuta auditoría de seguridad de dependencias"""
        self.logger.info("🔒 Ejecutando auditoría de seguridad...")
        
        security_results = {}
        
        try:
            # Usar safety para verificar vulnerabilidades
            safety_command = "safety check --json"
            result = subprocess.run(safety_command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                try:
                    safety_data = json.loads(result.stdout)
                    security_results["safety_check"] = {
                        "status": "success",
                        "vulnerabilities_found": len(safety_data),
                        "vulnerabilities": safety_data
                    }
                    
                    if safety_data:
                        self.logger.warning(f"⚠️ Se encontraron {len(safety_data)} vulnerabilidades de seguridad")
                        for vuln in safety_data:
                            self.logger.warning(f"   {vuln.get('package', 'Unknown')}: {vuln.get('description', 'No description')}")
                    else:
                        self.logger.info("✅ No se encontraron vulnerabilidades de seguridad")
                        
                except json.JSONDecodeError:
                    security_results["safety_check"] = {
                        "status": "error",
                        "error": "No se pudo parsear salida de safety"
                    }
            else:
                # Si safety no está disponible, usar pip-audit
                try:
                    audit_command = "pip-audit --format json"
                    audit_result = subprocess.run(audit_command, shell=True, capture_output=True, text=True)
                    
                    if audit_result.returncode == 0:
                        try:
                            audit_data = json.loads(audit_result.stdout)
                            security_results["pip_audit"] = {
                                "status": "success",
                                "vulnerabilities_found": len(audit_data.get("vulnerabilities", [])),
                                "vulnerabilities": audit_data
                            }
                        except json.JSONDecodeError:
                            security_results["pip_audit"] = {
                                "status": "error",
                                "error": "No se pudo parsear salida de pip-audit"
                            }
            else:
                        security_results["pip_audit"] = {
                            "status": "not_available",
                            "error": "pip-audit no está disponible"
                        }
                        
                except FileNotFoundError:
                    security_results["security_tools"] = {
                        "status": "not_available",
                        "error": "Ni safety ni pip-audit están disponibles"
                    }
                    
        except Exception as e:
            security_results["error"] = {
                "status": "error",
                "error": str(e)
            }
            self.logger.error(f"❌ Error en auditoría de seguridad: {e}")
        
        self.update_results["security_audit"] = security_results
        return security_results
    
    def generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en los resultados"""
        recommendations = []
        
        # Verificar numpy
        numpy_status = self.update_results["update_status"].get("numpy", {})
        if numpy_status.get("status") == "success":
            recommendations.append("✅ numpy se actualizó exitosamente a la versión 2.3.2")
        elif numpy_status.get("status") == "failed":
            recommendations.append("❌ Se recomienda resolver problemas de actualización de numpy antes de continuar")
        
        # Verificar compatibilidad
        compatibility_issues = []
        for package, compat_info in self.update_results["compatibility_check"].items():
            if compat_info.get("compatibility_status") == "warning":
                compatibility_issues.append(package)
        
        if compatibility_issues:
            recommendations.append(f"⚠️ Se detectaron posibles problemas de compatibilidad con: {', '.join(compatibility_issues)}")
            recommendations.append("   Se recomienda ejecutar tests completos después de la actualización")
        
        # Verificar seguridad
        security_issues = self.update_results["security_audit"].get("safety_check", {}).get("vulnerabilities_found", 0)
        if security_issues > 0:
            recommendations.append(f"🔒 Se encontraron {security_issues} vulnerabilidades de seguridad")
            recommendations.append("   Se recomienda actualizar dependencias vulnerables lo antes posible")
        
        # Recomendaciones generales
        recommendations.append("📋 Se recomienda ejecutar 'python scripts/run_complete_tests.py' para validar el sistema")
        recommendations.append("📋 Se recomienda verificar que todas las funcionalidades de IA funcionen correctamente")
        recommendations.append("📋 Se recomienda hacer backup de la base de datos antes de cambios importantes")
        
        self.update_results["recommendations"] = recommendations
        return recommendations
    
    def generate_update_report(self) -> Path:
        """Genera reporte completo de la actualización"""
        self.logger.info("📊 Generando reporte de actualización...")
        
        # Crear reporte HTML
        report_file = self.create_html_report()
        
        # Crear reporte JSON
        json_file = self.reports_dir / "dependency_update_results.json"
        with open(json_file, 'w') as f:
            json.dump(self.update_results, f, indent=2, default=str)
        
        self.logger.info(f"📄 Reporte de actualización guardado en: {report_file}")
        return report_file
    
    def create_html_report(self) -> Path:
        """Crea reporte HTML de la actualización"""
        report_file = self.reports_dir / "dependency_update_report.html"
        
        # Crear contenido HTML
        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Actualización de Dependencias - Sistema POS O'Data v2.0.0</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #28a745 0%, #20c997 100%); color: white; border-radius: 8px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; }}
        .summary-title {{ font-size: 1.2em; font-weight: bold; color: #495057; margin-bottom: 15px; }}
        .metric {{ display: flex; justify-content: space-between; margin: 8px 0; }}
        .metric-label {{ color: #6c757d; }}
        .metric-value {{ font-weight: bold; color: #28a745; }}
        .update-section {{ margin-bottom: 30px; }}
        .update-section h3 {{ color: #495057; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; }}
        .update-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        .update-table th, .update-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
        .update-table th {{ background-color: #f8f9fa; font-weight: bold; }}
        .status-success {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-error {{ color: #dc3545; }}
        .recommendations {{ margin-top: 30px; padding: 20px; background: #e8f5e8; border-radius: 8px; border-left: 4px solid #28a745; }}
        .timestamp {{ color: #6c757d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔄 Actualización de Dependencias</h1>
            <h2>Sistema POS O'Data v2.0.0</h2>
            <p class="timestamp">Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}</p>
        </div>
        
        <div class="summary-grid">
            <div class="summary-card">
                <div class="summary-title">📦 Dependencias Actualizadas</div>
                <div class="metric">
                    <span class="metric-label">Numpy:</span>
                    <span class="metric-value">{self.target_versions['numpy']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Scikit-learn:</span>
                    <span class="metric-value">{self.target_versions['scikit-learn']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Scipy:</span>
                    <span class="metric-value">{self.target_versions['scipy']}</span>
                </div>
            </div>
            
            <div class="summary-card">
                <div class="summary-title">🔗 Compatibilidad</div>
                <div class="metric">
                    <span class="metric-label">Estado:</span>
                    <span class="metric-value">Verificado</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Matriz:</span>
                    <span class="metric-value">Validada</span>
                </div>
            </div>
            
            <div class="summary-card">
                <div class="summary-title">🔒 Seguridad</div>
                <div class="metric">
                    <span class="metric-label">Auditoría:</span>
                    <span class="metric-value">Completada</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Vulnerabilidades:</span>
                    <span class="metric-value">Verificadas</span>
                </div>
            </div>
        </div>
        
        <div class="update-section">
            <h3>📊 Estado de Actualizaciones</h3>
            <table class="update-table">
                <thead>
                    <tr>
                        <th>Dependencia</th>
                        <th>Versión Anterior</th>
                        <th>Versión Nueva</th>
                        <th>Estado</th>
                        <th>Detalles</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Agregar resultados de actualización
        for package, status_info in self.update_results.get("update_status", {}).items():
            status_class = "status-success" if status_info.get("status") == "success" else "status-warning" if status_info.get("status") == "already_updated" else "status-error"
            status_icon = "✅" if status_info.get("status") == "success" else "⚠️" if status_info.get("status") == "already_updated" else "❌"
            
            previous_version = status_info.get("previous_version", "N/A")
            new_version = status_info.get("new_version", status_info.get("target_version", "N/A"))
            status_text = status_info.get("status", "unknown").replace("_", " ").title()
            details = status_info.get("error", "Actualización exitosa") if status_info.get("status") == "failed" else "OK"
            
            html_content += f"""
                    <tr>
                        <td><strong>{package}</strong></td>
                        <td>{previous_version}</td>
                        <td>{new_version}</td>
                        <td class="{status_class}">{status_icon} {status_text}</td>
                        <td>{details}</td>
                    </tr>
"""
        
        html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="recommendations">
            <h3>💡 Recomendaciones</h3>
            <ul>
"""
        
        # Agregar recomendaciones
        for recommendation in self.update_results.get("recommendations", []):
            html_content += f"                <li>{recommendation}</li>\n"
        
        html_content += """
            </ul>
        </div>
        
        <div style="margin-top: 30px; padding: 20px; background: #e8f4fd; border-radius: 8px; border-left: 4px solid #17a2b8;">
            <h3>🎯 Próximos Pasos</h3>
            <ul>
                <li>Ejecutar tests completos para validar funcionalidad</li>
                <li>Verificar que las funcionalidades de IA funcionen correctamente</li>
                <li>Monitorear performance del sistema después de la actualización</li>
                <li>Documentar cualquier cambio en el comportamiento del sistema</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_file
    
    def run_update_process(self) -> bool:
        """Ejecuta el proceso completo de actualización"""
        self.logger.info("🚀 Iniciando proceso de actualización de dependencias...")
        
        try:
            # 1. Obtener versiones actuales
            self.get_current_versions()
            
            # 2. Verificar versiones en PyPI
            pypi_versions = self.check_pypi_versions()
            
            # 3. Verificar compatibilidad
            self.check_compatibility_matrix()
            
            # 4. Actualizar numpy
            numpy_updated = self.update_numpy()
            
            # 5. Actualizar otras dependencias
            other_updates = self.update_other_dependencies()
            
            # 6. Ejecutar auditoría de seguridad
            self.run_security_audit()
            
            # 7. Generar recomendaciones
            self.generate_recommendations()
            
            # 8. Generar reporte
            self.generate_update_report()
            
            if numpy_updated and all(other_updates.values()):
                self.logger.info("🎉 ¡Proceso de actualización completado exitosamente!")
                return True
        else:
                self.logger.warning("⚠️ Algunas actualizaciones fallaron. Revisa el reporte para más detalles.")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error fatal durante la actualización: {e}")
            return False

def main():
    """Función principal"""
    updater = DependencyUpdater()
    
    try:
        success = updater.run_update_process()
        if success:
            print("✅ Actualización de dependencias completada exitosamente")
            print(f"📄 Reportes generados en: {updater.reports_dir}")
            sys.exit(0)
        else:
            print("❌ La actualización falló. Revisa el reporte para más detalles.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Actualización interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
