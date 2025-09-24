#!/usr/bin/env python3
"""
Script de Validación de Calidad Empresarial
Validación completa de todas las mejoras de calidad implementadas
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging

# Configurar logging para el script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/quality_validation.log')
    ]
)

logger = logging.getLogger(__name__)

class QualityValidator:
    """Validador de calidad del sistema"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results = {
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.2-hybrid',
            'tests': {},
            'metrics': {},
            'overall_score': 0
        }
    
    def run_complete_validation(self) -> Dict[str, Any]:
        """Ejecutar validación completa del sistema"""
        
        logger.info("🔍 Iniciando validación completa de calidad...")
        
        # 1. Validación de código
        self._validate_code_quality()
        
        # 2. Validación de seguridad
        self._validate_security()
        
        # 3. Validación de rendimiento
        self._validate_performance()
        
        # 4. Validación de endpoints
        self._validate_endpoints()
        
        # 5. Validación de base de datos
        self._validate_database()
        
        # 6. Validación de Docker
        self._validate_docker()
        
        # 7. Validación de métricas
        self._validate_metrics()
        
        # 8. Calcular puntuación general
        self._calculate_overall_score()
        
        logger.info(f"✅ Validación completada - Puntuación: {self.results['overall_score']}/100")
        
        return self.results
    
    def _validate_code_quality(self):
        """Validar calidad del código"""
        logger.info("📋 Validando calidad del código...")
        
        tests = {}
        
        # Ejecutar tests
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/', '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=300
            )
            tests['pytest'] = {
                'passed': result.returncode == 0,
                'output': result.stdout,
                'errors': result.stderr
            }
        except Exception as e:
            tests['pytest'] = {'passed': False, 'error': str(e)}
        
        # Verificar estructura de archivos críticos
        critical_files = [
            'app/core/exceptions.py',
            'app/core/validators.py',
            'app/core/logging_config.py',
            'app/core/metrics.py',
            'app/core/security_config.py'
        ]
        
        tests['file_structure'] = {
            'passed': all(os.path.exists(f) for f in critical_files),
            'missing_files': [f for f in critical_files if not os.path.exists(f)]
        }
        
        self.results['tests']['code_quality'] = tests
    
    def _validate_security(self):
        """Validar configuraciones de seguridad"""
        logger.info("🔒 Validando seguridad...")
        
        tests = {}
        
        # Test de headers de seguridad
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            required_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection',
                'Content-Security-Policy'
            ]
            
            missing_headers = [h for h in required_headers if h not in response.headers]
            
            tests['security_headers'] = {
                'passed': len(missing_headers) == 0,
                'missing_headers': missing_headers,
                'present_headers': list(response.headers.keys())
            }
            
        except Exception as e:
            tests['security_headers'] = {'passed': False, 'error': str(e)}
        
        # Test de autenticación
        try:
            auth_response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={'username': 'admin', 'password': 'admin'},
                timeout=10
            )
            
            tests['authentication'] = {
                'passed': auth_response.status_code == 200,
                'status_code': auth_response.status_code,
                'has_token': 'access_token' in auth_response.text
            }
            
        except Exception as e:
            tests['authentication'] = {'passed': False, 'error': str(e)}
        
        # Test de protección contra inyección SQL
        try:
            malicious_payload = {
                'username': "admin'; DROP TABLE users; --",
                'password': 'admin'
            }
            
            injection_response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json=malicious_payload,
                timeout=10
            )
            
            # Debe rechazar la entrada maliciosa
            tests['sql_injection_protection'] = {
                'passed': injection_response.status_code in [400, 422],
                'status_code': injection_response.status_code
            }
            
        except Exception as e:
            tests['sql_injection_protection'] = {'passed': False, 'error': str(e)}
        
        self.results['tests']['security'] = tests
    
    def _validate_performance(self):
        """Validar rendimiento del sistema"""
        logger.info("⚡ Validando rendimiento...")
        
        tests = {}
        
        # Test de tiempo de respuesta
        endpoints_to_test = [
            '/health',
            '/ai-test',
            '/'
        ]
        
        response_times = {}
        
        for endpoint in endpoints_to_test:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                duration = time.time() - start_time
                
                response_times[endpoint] = {
                    'duration': duration,
                    'status_code': response.status_code,
                    'passed': duration < 1.0 and response.status_code == 200
                }
                
            except Exception as e:
                response_times[endpoint] = {
                    'passed': False,
                    'error': str(e)
                }
        
        tests['response_times'] = response_times
        
        # Test de carga básica
        try:
            start_time = time.time()
            concurrent_requests = []
            
            import threading
            
            def make_request():
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=5)
                    concurrent_requests.append(response.status_code)
                except:
                    concurrent_requests.append(0)
            
            # 10 requests concurrentes
            threads = []
            for _ in range(10):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            duration = time.time() - start_time
            successful_requests = sum(1 for status in concurrent_requests if status == 200)
            
            tests['load_test'] = {
                'passed': successful_requests >= 8,  # 80% éxito mínimo
                'successful_requests': successful_requests,
                'total_requests': 10,
                'total_duration': duration,
                'avg_duration': duration / 10
            }
            
        except Exception as e:
            tests['load_test'] = {'passed': False, 'error': str(e)}
        
        self.results['tests']['performance'] = tests
    
    def _validate_endpoints(self):
        """Validar endpoints críticos"""
        logger.info("🌐 Validando endpoints...")
        
        endpoints = {
            'health_basic': {'method': 'GET', 'url': '/health', 'expected': 200},
            'health_ai': {'method': 'GET', 'url': '/ai-test', 'expected': 200},
            'api_root': {'method': 'GET', 'url': '/', 'expected': 200},
            'metrics': {'method': 'GET', 'url': '/metrics', 'expected': 200},
            'auth_login': {
                'method': 'POST', 
                'url': '/api/v1/auth/login',
                'data': {'username': 'admin', 'password': 'admin'},
                'expected': 200
            }
        }
        
        tests = {}
        
        for name, config in endpoints.items():
            try:
                if config['method'] == 'GET':
                    response = requests.get(f"{self.base_url}{config['url']}", timeout=10)
                elif config['method'] == 'POST':
                    response = requests.post(
                        f"{self.base_url}{config['url']}",
                        json=config.get('data'),
                        timeout=10
                    )
                
                tests[name] = {
                    'passed': response.status_code == config['expected'],
                    'status_code': response.status_code,
                    'expected': config['expected'],
                    'response_time': response.elapsed.total_seconds()
                }
                
            except Exception as e:
                tests[name] = {'passed': False, 'error': str(e)}
        
        self.results['tests']['endpoints'] = tests
    
    def _validate_database(self):
        """Validar estado de la base de datos"""
        logger.info("🗄️ Validando base de datos...")
        
        tests = {}
        
        # Verificar conexión a PostgreSQL
        try:
            result = subprocess.run(
                ['docker', 'exec', 'pos-odata-db', 'pg_isready', '-U', 'pos_user'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            tests['connection'] = {
                'passed': result.returncode == 0,
                'output': result.stdout
            }
            
        except Exception as e:
            tests['connection'] = {'passed': False, 'error': str(e)}
        
        # Verificar tablas principales
        try:
            result = subprocess.run([
                'docker', 'exec', '-e', 'PGPASSWORD=4QRju1YLSF_gHOW9oRnxxg',
                'pos-odata-db', 'psql', '-U', 'pos_user', '-d', 'pos_db_production',
                '-c', "SELECT tablename FROM pg_tables WHERE schemaname='public';"
            ], capture_output=True, text=True, timeout=30)
            
            expected_tables = ['users', 'products', 'sales', 'inventory', 'customers']
            output = result.stdout
            
            tests['tables'] = {
                'passed': all(table in output for table in expected_tables),
                'found_tables': output.split('\n') if result.returncode == 0 else [],
                'expected_tables': expected_tables
            }
            
        except Exception as e:
            tests['tables'] = {'passed': False, 'error': str(e)}
        
        self.results['tests']['database'] = tests
    
    def _validate_docker(self):
        """Validar contenedores Docker"""
        logger.info("🐳 Validando Docker...")
        
        tests = {}
        
        # Verificar contenedores activos
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', 'name=pos-odata', '--format', 'json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parsear salida JSON de Docker
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            containers.append(json.loads(line))
                        except:
                            pass
                
                expected_containers = ['pos-odata-app', 'pos-odata-db', 'pos-odata-redis']
                running_containers = [c.get('Names', '') for c in containers]
                
                tests['containers'] = {
                    'passed': len(containers) >= 3,
                    'running_containers': running_containers,
                    'expected_containers': expected_containers,
                    'container_count': len(containers)
                }
            else:
                tests['containers'] = {'passed': False, 'error': result.stderr}
                
        except Exception as e:
            tests['containers'] = {'passed': False, 'error': str(e)}
        
        self.results['tests']['docker'] = tests
    
    def _validate_metrics(self):
        """Validar sistema de métricas"""
        logger.info("📊 Validando métricas...")
        
        tests = {}
        
        # Test de endpoint de métricas
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=10)
            
            tests['metrics_endpoint'] = {
                'passed': response.status_code == 200,
                'status_code': response.status_code,
                'content_type': response.headers.get('Content-Type', ''),
                'has_metrics': 'TYPE' in response.text
            }
            
        except Exception as e:
            tests['metrics_endpoint'] = {'passed': False, 'error': str(e)}
        
        # Test de health check detallado
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code in [200, 503]:
                data = response.json()
                
                tests['health_detailed'] = {
                    'passed': 'overall' in data,
                    'has_timestamp': 'timestamp' in data.get('overall', {}),
                    'structure': list(data.keys())
                }
            else:
                tests['health_detailed'] = {
                    'passed': False,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            tests['health_detailed'] = {'passed': False, 'error': str(e)}
        
        self.results['tests']['metrics'] = tests
    
    def _calculate_overall_score(self):
        """Calcular puntuación general de calidad"""
        
        total_tests = 0
        passed_tests = 0
        
        def count_tests(test_dict):
            nonlocal total_tests, passed_tests
            
            for key, value in test_dict.items():
                if isinstance(value, dict):
                    if 'passed' in value:
                        total_tests += 1
                        if value['passed']:
                            passed_tests += 1
                    else:
                        count_tests(value)
        
        count_tests(self.results['tests'])
        
        if total_tests > 0:
            score = int((passed_tests / total_tests) * 100)
        else:
            score = 0
        
        self.results['overall_score'] = score
        self.results['test_summary'] = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': f"{score}%"
        }
    
    def generate_report(self) -> str:
        """Generar reporte de calidad en formato markdown"""
        
        report = f"""# 📊 Reporte de Calidad - Sistema POS O'Data v2.0.2

## 🎯 Resumen Ejecutivo

**Fecha**: {self.results['timestamp']}  
**Versión**: {self.results['version']}  
**Puntuación General**: {self.results['overall_score']}/100  

### 📋 Resumen de Tests
- **Total de Tests**: {self.results['test_summary']['total_tests']}
- **Tests Exitosos**: {self.results['test_summary']['passed_tests']}
- **Tests Fallidos**: {self.results['test_summary']['failed_tests']}
- **Tasa de Éxito**: {self.results['test_summary']['success_rate']}

---

## 📊 Resultados Detallados

"""
        
        # Agregar resultados por categoría
        for category, tests in self.results['tests'].items():
            report += f"### {category.title()}\n\n"
            
            for test_name, result in tests.items():
                status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
                report += f"- **{test_name}**: {status}\n"
                
                if not result.get('passed', False) and 'error' in result:
                    report += f"  - Error: {result['error']}\n"
            
            report += "\n"
        
        return report
    
    def save_report(self, filename: str = None):
        """Guardar reporte de calidad"""
        
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"reports/quality_report_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Guardar también en formato markdown
        md_filename = filename.replace('.json', '.md')
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(self.generate_report())
        
        logger.info(f"📄 Reporte guardado en: {filename} y {md_filename}")

def main():
    """Función principal del script"""
    
    print("🔍 Sistema de Validación de Calidad Empresarial")
    print("=" * 50)
    
    # Verificar que el sistema esté corriendo
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        print(f"✅ Sistema detectado - Status: {response.status_code}")
    except:
        print("❌ Sistema no está corriendo. Iniciando Docker...")
        try:
            subprocess.run(['docker', 'compose', '-f', 'docker-compose.production.yml', 'up', '-d'], 
                         timeout=120)
            time.sleep(30)  # Esperar que los servicios inicien
        except Exception as e:
            print(f"❌ Error iniciando sistema: {e}")
            sys.exit(1)
    
    # Ejecutar validación
    validator = QualityValidator()
    results = validator.run_complete_validation()
    
    # Guardar reporte
    validator.save_report()
    
    # Mostrar resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("=" * 50)
    print(f"Puntuación General: {results['overall_score']}/100")
    print(f"Tests Exitosos: {results['test_summary']['passed_tests']}/{results['test_summary']['total_tests']}")
    print(f"Tasa de Éxito: {results['test_summary']['success_rate']}")
    
    # Determinar nivel de calidad
    score = results['overall_score']
    if score >= 90:
        print("🏆 CALIDAD: EXCELENTE")
    elif score >= 80:
        print("✅ CALIDAD: BUENA")
    elif score >= 70:
        print("⚠️ CALIDAD: ACEPTABLE")
    else:
        print("❌ CALIDAD: NECESITA MEJORAS")
    
    return results['overall_score']

if __name__ == "__main__":
    exit_code = 0 if main() >= 70 else 1
    sys.exit(exit_code)
