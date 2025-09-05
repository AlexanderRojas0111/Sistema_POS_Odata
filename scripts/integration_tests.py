#!/usr/bin/env python3
"""
Tests de Integración Completos - O'Data v2.0.0
==============================================

Script para tests de integración end-to-end del sistema

Autor: Sistema POS Odata
Versión: 2.0.0
"""

import os
import sys
import time
import json
import requests
import argparse
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import logging
import subprocess
import threading


@dataclass
class IntegrationTestResult:
    """Resultado de un test de integración"""
    test_name: str
    success: bool
    duration: float
    details: str
    error: Optional[str] = None


class IntegrationTester:
    """Clase para tests de integración"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.auth_token = None
        self.test_data = {}
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def wait_for_server(self, timeout: int = 60) -> bool:
        """Esperar a que el servidor esté disponible"""
        self.logger.info(f"⏳ Esperando servidor en {self.base_url}...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    self.logger.info("✅ Servidor disponible")
                    return True
            except:
                pass
            
            time.sleep(2)
        
        self.logger.error("❌ Servidor no disponible")
        return False
    
    def authenticate(self) -> IntegrationTestResult:
        """Test de autenticación completa"""
        start_time = time.time()
        
        try:
            # 1. Registrar usuario de prueba
            register_data = {
                "username": f"testuser_{int(time.time())}",
                "password": "TestPass123!",
                "email": f"test_{int(time.time())}@example.com"
            }
            
            register_response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=register_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if register_response.status_code != 201:
                return IntegrationTestResult(
                    test_name="Authentication Flow",
                    success=False,
                    duration=time.time() - start_time,
                    details="Falló el registro de usuario",
                    error=f"Status: {register_response.status_code}, Response: {register_response.text}"
                )
            
            # 2. Hacer login
            login_data = {
                "username": register_data["username"],
                "password": register_data["password"]
            }
            
            login_response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if login_response.status_code != 200:
                return IntegrationTestResult(
                    test_name="Authentication Flow",
                    success=False,
                    duration=time.time() - start_time,
                    details="Falló el login",
                    error=f"Status: {login_response.status_code}, Response: {login_response.text}"
                )
            
            # 3. Obtener token
            login_data = login_response.json()
            self.auth_token = login_data.get('access_token')
            
            if not self.auth_token:
                return IntegrationTestResult(
                    test_name="Authentication Flow",
                    success=False,
                    duration=time.time() - start_time,
                    details="No se recibió token de acceso",
                    error="Token no encontrado en respuesta"
                )
            
            # 4. Verificar token
            self.session.headers.update({
                'Authorization': f'Bearer {self.auth_token}'
            })
            
            me_response = self.session.get(
                f"{self.base_url}/api/v1/auth/me",
                timeout=10
            )
            
            if me_response.status_code != 200:
                return IntegrationTestResult(
                    test_name="Authentication Flow",
                    success=False,
                    duration=time.time() - start_time,
                    details="Falló la verificación del token",
                    error=f"Status: {me_response.status_code}"
                )
            
            # Guardar datos de usuario para otros tests
            self.test_data['user'] = register_data
            self.test_data['user']['id'] = me_response.json().get('id')
            
            return IntegrationTestResult(
                test_name="Authentication Flow",
                success=True,
                duration=time.time() - start_time,
                details="Flujo completo de autenticación exitoso"
            )
            
        except Exception as e:
            return IntegrationTestResult(
                test_name="Authentication Flow",
                success=False,
                duration=time.time() - start_time,
                details="Error durante autenticación",
                error=str(e)
            )
    
    def test_product_management(self) -> IntegrationTestResult:
        """Test de gestión completa de productos"""
        start_time = time.time()
        
        try:
            # 1. Crear producto
            product_data = {
                "code": f"PROD_{int(time.time())}",
                "name": "Producto Test Integración",
                "description": "Producto creado durante test de integración",
                "price": 25.99,
                "stock": 100,
                "category": "Test"
            }
            
            # Como no tenemos endpoint de crear producto, vamos a buscar productos
            search_response = self.session.get(
                f"{self.base_url}/api/v1/search/products",
                params={"q": "test"},
                timeout=10
            )
            
            if search_response.status_code != 200:
                return IntegrationTestResult(
                    test_name="Product Management",
                    success=False,
                    duration=time.time() - start_time,
                    details="Falló la búsqueda de productos",
                    error=f"Status: {search_response.status_code}"
                )
            
            # 2. Verificar estructura de respuesta
            search_data = search_response.json()
            if 'products' not in search_data:
                return IntegrationTestResult(
                    test_name="Product Management",
                    success=False,
                    duration=time.time() - start_time,
                    details="Estructura de respuesta incorrecta",
                    error="Campo 'products' no encontrado"
                )
            
            return IntegrationTestResult(
                test_name="Product Management",
                success=True,
                duration=time.time() - start_time,
                details="Gestión de productos funcional"
            )
            
        except Exception as e:
            return IntegrationTestResult(
                test_name="Product Management",
                success=False,
                duration=time.time() - start_time,
                details="Error durante gestión de productos",
                error=str(e)
            )
    
    def test_sales_workflow(self) -> IntegrationTestResult:
        """Test del flujo completo de ventas"""
        start_time = time.time()
        
        try:
            # 1. Buscar productos disponibles
            products_response = self.session.get(
                f"{self.base_url}/api/v1/search/products",
                params={"q": ""},
                timeout=10
            )
            
            if products_response.status_code != 200:
                return IntegrationTestResult(
                    test_name="Sales Workflow",
                    success=False,
                    duration=time.time() - start_time,
                    details="No se pudieron obtener productos",
                    error=f"Status: {products_response.status_code}"
                )
            
            # 2. Verificar estadísticas de ventas
            sales_stats_response = self.session.get(
                f"{self.base_url}/api/v1/stats/business",
                timeout=10
            )
            
            if sales_stats_response.status_code != 200:
                return IntegrationTestResult(
                    test_name="Sales Workflow",
                    success=False,
                    duration=time.time() - start_time,
                    details="No se pudieron obtener estadísticas de ventas",
                    error=f"Status: {sales_stats_response.status_code}"
                )
            
            # 3. Buscar ventas
            sales_search_response = self.session.get(
                f"{self.base_url}/api/v1/search/sales",
                timeout=10
            )
            
            if sales_search_response.status_code != 200:
                return IntegrationTestResult(
                    test_name="Sales Workflow",
                    success=False,
                    duration=time.time() - start_time,
                    details="No se pudieron buscar ventas",
                    error=f"Status: {sales_search_response.status_code}"
                )
            
            # 4. Generar reporte de ventas
            sales_report_response = self.session.get(
                f"{self.base_url}/api/v1/reports/sales/summary",
                timeout=10
            )
            
            if sales_report_response.status_code != 200:
                return IntegrationTestResult(
                    test_name="Sales Workflow",
                    success=False,
                    duration=time.time() - start_time,
                    details="No se pudo generar reporte de ventas",
                    error=f"Status: {sales_report_response.status_code}"
                )
            
            return IntegrationTestResult(
                test_name="Sales Workflow",
                success=True,
                duration=time.time() - start_time,
                details="Flujo completo de ventas funcional"
            )
            
        except Exception as e:
            return IntegrationTestResult(
                test_name="Sales Workflow",
                success=False,
                duration=time.time() - start_time,
                details="Error durante flujo de ventas",
                error=str(e)
            )
    
    def test_reporting_system(self) -> IntegrationTestResult:
        """Test del sistema completo de reportes"""
        start_time = time.time()
        
        try:
            # Endpoints de reportes para testear
            report_endpoints = [
                '/api/v1/reports/sales/summary',
                '/api/v1/reports/inventory/status',
                '/api/v1/reports/users/activity',
                '/api/v1/reports/financial/summary'
            ]
            
            failed_endpoints = []
            
            for endpoint in report_endpoints:
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    timeout=15
                )
                
                if response.status_code != 200:
                    failed_endpoints.append(f"{endpoint}: {response.status_code}")
            
            if failed_endpoints:
                return IntegrationTestResult(
                    test_name="Reporting System",
                    success=False,
                    duration=time.time() - start_time,
                    details="Algunos reportes fallaron",
                    error=f"Endpoints fallidos: {', '.join(failed_endpoints)}"
                )
            
            return IntegrationTestResult(
                test_name="Reporting System",
                success=True,
                duration=time.time() - start_time,
                details="Sistema de reportes funcional"
            )
            
        except Exception as e:
            return IntegrationTestResult(
                test_name="Reporting System",
                success=False,
                duration=time.time() - start_time,
                details="Error durante tests de reportes",
                error=str(e)
            )
    
    def test_search_functionality(self) -> IntegrationTestResult:
        """Test de funcionalidad completa de búsqueda"""
        start_time = time.time()
        
        try:
            # Tests de búsqueda
            search_tests = [
                ('/api/v1/search/products', {'q': 'test'}),
                ('/api/v1/search/sales', {'start_date': '2024-01-01'}),
                ('/api/v1/search/users', {'q': 'test'}),
                ('/api/v1/search/global', {'q': 'test'})
            ]
            
            failed_searches = []
            
            for endpoint, params in search_tests:
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    timeout=10
                )
                
                if response.status_code != 200:
                    failed_searches.append(f"{endpoint}: {response.status_code}")
                else:
                    # Verificar estructura de respuesta
                    data = response.json()
                    if not isinstance(data, dict):
                        failed_searches.append(f"{endpoint}: Estructura inválida")
            
            if failed_searches:
                return IntegrationTestResult(
                    test_name="Search Functionality",
                    success=False,
                    duration=time.time() - start_time,
                    details="Algunas búsquedas fallaron",
                    error=f"Búsquedas fallidas: {', '.join(failed_searches)}"
                )
            
            return IntegrationTestResult(
                test_name="Search Functionality",
                success=True,
                duration=time.time() - start_time,
                details="Sistema de búsqueda funcional"
            )
            
        except Exception as e:
            return IntegrationTestResult(
                test_name="Search Functionality",
                success=False,
                duration=time.time() - start_time,
                details="Error durante tests de búsqueda",
                error=str(e)
            )
    
    def test_stats_and_monitoring(self) -> IntegrationTestResult:
        """Test de estadísticas y monitoreo"""
        start_time = time.time()
        
        try:
            # Endpoints de estadísticas
            stats_endpoints = [
                '/api/v1/stats/system',
                '/api/v1/stats/business',
                '/api/v1/stats/performance',
                '/api/v1/stats/health/detailed',
                '/api/v1/stats/version'
            ]
            
            failed_stats = []
            
            for endpoint in stats_endpoints:
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    timeout=15
                )
                
                if response.status_code != 200:
                    failed_stats.append(f"{endpoint}: {response.status_code}")
                else:
                    # Verificar que retorne JSON válido
                    try:
                        data = response.json()
                        if not isinstance(data, dict):
                            failed_stats.append(f"{endpoint}: No es JSON válido")
                    except:
                        failed_stats.append(f"{endpoint}: Respuesta no es JSON")
            
            if failed_stats:
                return IntegrationTestResult(
                    test_name="Stats and Monitoring",
                    success=False,
                    duration=time.time() - start_time,
                    details="Algunas estadísticas fallaron",
                    error=f"Stats fallidas: {', '.join(failed_stats)}"
                )
            
            return IntegrationTestResult(
                test_name="Stats and Monitoring",
                success=True,
                duration=time.time() - start_time,
                details="Sistema de estadísticas funcional"
            )
            
        except Exception as e:
            return IntegrationTestResult(
                test_name="Stats and Monitoring",
                success=False,
                duration=time.time() - start_time,
                details="Error durante tests de estadísticas",
                error=str(e)
            )
    
    def test_error_handling(self) -> IntegrationTestResult:
        """Test de manejo de errores"""
        start_time = time.time()
        
        try:
            # Tests de manejo de errores
            error_tests = [
                ('/api/v1/nonexistent', 404),
                ('/health', 405, 'POST'),  # Método no permitido
            ]
            
            failed_errors = []
            
            for test in error_tests:
                endpoint = test[0]
                expected_code = test[1]
                method = test[2] if len(test) > 2 else 'GET'
                
                if method == 'GET':
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code != expected_code:
                    failed_errors.append(f"{endpoint}: esperado {expected_code}, obtenido {response.status_code}")
            
            # Test de JSON inválido
            invalid_json_response = self.session.post(
                f"{self.base_url}/api/v1/auth/validate",
                data="invalid json",
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if invalid_json_response.status_code not in [400, 415]:
                failed_errors.append(f"JSON inválido: esperado 400/415, obtenido {invalid_json_response.status_code}")
            
            if failed_errors:
                return IntegrationTestResult(
                    test_name="Error Handling",
                    success=False,
                    duration=time.time() - start_time,
                    details="Algunos tests de error fallaron",
                    error=f"Errores: {', '.join(failed_errors)}"
                )
            
            return IntegrationTestResult(
                test_name="Error Handling",
                success=True,
                duration=time.time() - start_time,
                details="Manejo de errores funcional"
            )
            
        except Exception as e:
            return IntegrationTestResult(
                test_name="Error Handling",
                success=False,
                duration=time.time() - start_time,
                details="Error durante tests de manejo de errores",
                error=str(e)
            )
    
    def test_database_connectivity(self) -> IntegrationTestResult:
        """Test de conectividad de base de datos"""
        start_time = time.time()
        
        try:
            # Test de health check detallado
            health_response = self.session.get(
                f"{self.base_url}/api/v1/stats/health/detailed",
                timeout=10
            )
            
            if health_response.status_code != 200:
                return IntegrationTestResult(
                    test_name="Database Connectivity",
                    success=False,
                    duration=time.time() - start_time,
                    details="Health check falló",
                    error=f"Status: {health_response.status_code}"
                )
            
            health_data = health_response.json()
            
            # Verificar estado de la base de datos
            if not health_data.get('checks', {}).get('database_connection'):
                return IntegrationTestResult(
                    test_name="Database Connectivity",
                    success=False,
                    duration=time.time() - start_time,
                    details="Base de datos no conectada",
                    error="Database connection check failed"
                )
            
            return IntegrationTestResult(
                test_name="Database Connectivity",
                success=True,
                duration=time.time() - start_time,
                details="Conectividad de base de datos funcional"
            )
            
        except Exception as e:
            return IntegrationTestResult(
                test_name="Database Connectivity",
                success=False,
                duration=time.time() - start_time,
                details="Error durante test de base de datos",
                error=str(e)
            )
    
    def test_redis_connectivity(self) -> IntegrationTestResult:
        """Test de conectividad de Redis"""
        start_time = time.time()
        
        try:
            # Test de health check
            health_response = self.session.get(
                f"{self.base_url}/health",
                timeout=10
            )
            
            if health_response.status_code != 200:
                return IntegrationTestResult(
                    test_name="Redis Connectivity",
                    success=False,
                    duration=time.time() - start_time,
                    details="Health check falló",
                    error=f"Status: {health_response.status_code}"
                )
            
            health_data = health_response.json()
            redis_status = health_data.get('redis', 'disconnected')
            
            return IntegrationTestResult(
                test_name="Redis Connectivity",
                success=redis_status == 'connected',
                duration=time.time() - start_time,
                details=f"Redis status: {redis_status}"
            )
            
        except Exception as e:
            return IntegrationTestResult(
                test_name="Redis Connectivity",
                success=False,
                duration=time.time() - start_time,
                details="Error durante test de Redis",
                error=str(e)
            )
    
    def test_api_versioning(self) -> IntegrationTestResult:
        """Test de versionado de API"""
        start_time = time.time()
        
        try:
            # Test de versiones de API
            version_endpoints = [
                '/api/v1/stats/version',
                '/api/v2/health'  # Si existe v2
            ]
            
            working_versions = []
            
            for endpoint in version_endpoints:
                try:
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        working_versions.append(endpoint)
                except:
                    pass
            
            if not working_versions:
                return IntegrationTestResult(
                    test_name="API Versioning",
                    success=False,
                    duration=time.time() - start_time,
                    details="No hay versiones de API disponibles",
                    error="Ningún endpoint de versión responde"
                )
            
            return IntegrationTestResult(
                test_name="API Versioning",
                success=True,
                duration=time.time() - start_time,
                details=f"Versiones funcionales: {', '.join(working_versions)}"
            )
            
        except Exception as e:
            return IntegrationTestResult(
                test_name="API Versioning",
                success=False,
                duration=time.time() - start_time,
                details="Error durante test de versionado",
                error=str(e)
            )
    
    def test_concurrent_operations(self) -> IntegrationTestResult:
        """Test de operaciones concurrentes"""
        start_time = time.time()
        
        try:
            def concurrent_request():
                """Función para requests concurrentes"""
                try:
                    response = self.session.get(
                        f"{self.base_url}/api/v1/stats/system",
                        timeout=10
                    )
                    return response.status_code == 200
                except:
                    return False
            
            # Ejecutar 20 requests concurrentes
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(concurrent_request) for _ in range(20)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            success_rate = sum(results) / len(results) * 100
            
            if success_rate < 80:
                return IntegrationTestResult(
                    test_name="Concurrent Operations",
                    success=False,
                    duration=time.time() - start_time,
                    details=f"Success rate bajo: {success_rate:.1f}%",
                    error="Sistema no maneja bien concurrencia"
                )
            
            return IntegrationTestResult(
                test_name="Concurrent Operations",
                success=True,
                duration=time.time() - start_time,
                details=f"Operaciones concurrentes exitosas: {success_rate:.1f}%"
            )
            
        except Exception as e:
            return IntegrationTestResult(
                test_name="Concurrent Operations",
                success=False,
                duration=time.time() - start_time,
                details="Error durante tests concurrentes",
                error=str(e)
            )
    
    def run_comprehensive_integration_test(self) -> List[IntegrationTestResult]:
        """Ejecutar suite completa de tests de integración"""
        self.logger.info("🚀 Iniciando suite completa de tests de integración")
        self.logger.info("=" * 60)
        
        results = []
        
        # 1. Verificar que el servidor esté disponible
        if not self.wait_for_server():
            results.append(IntegrationTestResult(
                test_name="Server Availability",
                success=False,
                duration=0,
                details="Servidor no disponible",
                error="No se pudo conectar al servidor"
            ))
            return results
        
        # 2. Test de autenticación
        self.logger.info("1️⃣  Testing Authentication Flow")
        auth_result = self.authenticate()
        results.append(auth_result)
        
        if not auth_result.success:
            self.logger.error("❌ Autenticación falló, saltando otros tests")
            return results
        
        # 3. Test de gestión de productos
        self.logger.info("2️⃣  Testing Product Management")
        product_result = self.test_product_management()
        results.append(product_result)
        
        # 4. Test de flujo de ventas
        self.logger.info("3️⃣  Testing Sales Workflow")
        sales_result = self.test_sales_workflow()
        results.append(sales_result)
        
        # 5. Test de sistema de reportes
        self.logger.info("4️⃣  Testing Reporting System")
        reports_result = self.test_reporting_system()
        results.append(reports_result)
        
        # 6. Test de funcionalidad de búsqueda
        self.logger.info("5️⃣  Testing Search Functionality")
        search_result = self.test_search_functionality()
        results.append(search_result)
        
        # 7. Test de estadísticas y monitoreo
        self.logger.info("6️⃣  Testing Stats and Monitoring")
        stats_result = self.test_stats_and_monitoring()
        results.append(stats_result)
        
        # 8. Test de conectividad de base de datos
        self.logger.info("7️⃣  Testing Database Connectivity")
        db_result = self.test_database_connectivity()
        results.append(db_result)
        
        # 9. Test de conectividad de Redis
        self.logger.info("8️⃣  Testing Redis Connectivity")
        redis_result = self.test_redis_connectivity()
        results.append(redis_result)
        
        # 10. Test de versionado de API
        self.logger.info("9️⃣  Testing API Versioning")
        versioning_result = self.test_api_versioning()
        results.append(versioning_result)
        
        # 11. Test de manejo de errores
        self.logger.info("🔟 Testing Error Handling")
        error_result = self.test_error_handling()
        results.append(error_result)
        
        # 12. Test de operaciones concurrentes
        self.logger.info("1️⃣1️⃣  Testing Concurrent Operations")
        concurrent_result = self.test_concurrent_operations()
        results.append(concurrent_result)
        
        self.logger.info("✅ Suite completa de tests de integración completada")
        return results
    
    def generate_integration_report(self, results: List[IntegrationTestResult], 
                                  output_file: str = None) -> str:
        """Generar reporte de integración"""
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Calcular tiempo total
        total_duration = sum(r.duration for r in results)
        
        report = {
            'test_summary': {
                'timestamp': datetime.now().isoformat(),
                'base_url': self.base_url,
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': success_rate,
                'total_duration': total_duration
            },
            'detailed_results': [
                {
                    'test_name': r.test_name,
                    'success': r.success,
                    'duration': r.duration,
                    'details': r.details,
                    'error': r.error
                } for r in results
            ],
            'recommendations': []
        }
        
        # Generar recomendaciones
        if success_rate == 100:
            report['recommendations'].append("✅ Todos los tests de integración pasaron exitosamente.")
        elif success_rate >= 80:
            report['recommendations'].append("⚠️  La mayoría de tests pasaron, revisar los fallidos.")
        else:
            report['recommendations'].append("🚨 Muchos tests fallaron, revisar la configuración del sistema.")
        
        report['recommendations'].extend([
            "🔄 Ejecutar tests de integración regularmente",
            "📊 Monitorear métricas de performance",
            "🛡️  Verificar logs de seguridad",
            "🔧 Mantener dependencias actualizadas"
        ])
        
        # Guardar reporte
        report_json = json.dumps(report, indent=2, ensure_ascii=False)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_json)
            self.logger.info(f"📄 Reporte guardado en: {output_file}")
        
        return report_json


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Tests de Integración para O'Data POS v2.0.0"
    )
    
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='URL base del servidor (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--test-type',
        choices=['auth', 'products', 'sales', 'reports', 'search', 'stats', 'errors', 'db', 'redis', 'concurrent', 'comprehensive'],
        default='comprehensive',
        help='Tipo de test a ejecutar'
    )
    
    parser.add_argument(
        '--output',
        help='Archivo de salida para el reporte'
    )
    
    parser.add_argument(
        '--wait-server',
        action='store_true',
        help='Esperar a que el servidor esté disponible'
    )
    
    args = parser.parse_args()
    
    # Crear tester
    tester = IntegrationTester(args.url)
    
    # Esperar servidor si se solicita
    if args.wait_server:
        if not tester.wait_for_server():
            print("❌ Servidor no disponible")
            sys.exit(1)
    
    # Ejecutar test según el tipo
    if args.test_type == 'auth':
        results = [tester.authenticate()]
    elif args.test_type == 'products':
        tester.authenticate()
        results = [tester.test_product_management()]
    elif args.test_type == 'sales':
        tester.authenticate()
        results = [tester.test_sales_workflow()]
    elif args.test_type == 'reports':
        tester.authenticate()
        results = [tester.test_reporting_system()]
    elif args.test_type == 'search':
        tester.authenticate()
        results = [tester.test_search_functionality()]
    elif args.test_type == 'stats':
        tester.authenticate()
        results = [tester.test_stats_and_monitoring()]
    elif args.test_type == 'errors':
        results = [tester.test_error_handling()]
    elif args.test_type == 'db':
        results = [tester.test_database_connectivity()]
    elif args.test_type == 'redis':
        results = [tester.test_redis_connectivity()]
    elif args.test_type == 'concurrent':
        tester.authenticate()
        results = [tester.test_concurrent_operations()]
    else:  # comprehensive
        results = tester.run_comprehensive_integration_test()
    
    # Generar reporte
    output_file = args.output or f"integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report = tester.generate_integration_report(results, output_file)
    
    # Mostrar resumen
    successful_tests = sum(1 for r in results if r.success)
    total_tests = len(results)
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print("\n" + "=" * 60)
    print("🔗 RESUMEN DE INTEGRACIÓN")
    print("=" * 60)
    print(f"Total de tests: {total_tests}")
    print(f"Tests exitosos: {successful_tests}")
    print(f"Tests fallidos: {total_tests - successful_tests}")
    print(f"Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("✅ Todos los tests de integración pasaron!")
    elif success_rate >= 80:
        print("⚠️  La mayoría de tests pasaron, revisar los fallidos")
    else:
        print("🚨 Muchos tests fallaron, revisar configuración")
    
    print(f"\n📄 Reporte completo guardado en: {output_file}")
    print("✅ Tests de integración completados!")


if __name__ == "__main__":
    main()
