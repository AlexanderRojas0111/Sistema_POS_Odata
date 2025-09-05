#!/usr/bin/env python3
"""
Tests de Performance y Carga - O'Data v2.0.0
============================================

Script para tests de stress, carga y performance del sistema

Autor: Sistema POS Odata
Versión: 2.0.0
"""

import os
import sys
import time
import json
import asyncio
import aiohttp
import requests
import statistics
import argparse
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Any
import logging


@dataclass
class PerformanceResult:
    """Resultado de un test de performance"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    success: bool
    error: str = None


class PerformanceTester:
    """Clase para tests de performance"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results: List[PerformanceResult] = []
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def test_endpoint(self, endpoint: str, method: str = 'GET', 
                     data: Dict = None, headers: Dict = None) -> PerformanceResult:
        """Test de un endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # en milisegundos
            
            return PerformanceResult(
                endpoint=endpoint,
                method=method,
                response_time=response_time,
                status_code=response.status_code,
                success=response.status_code < 400
            )
            
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return PerformanceResult(
                endpoint=endpoint,
                method=method,
                response_time=response_time,
                status_code=0,
                success=False,
                error=str(e)
            )
    
    def load_test(self, endpoint: str, concurrent_users: int = 10, 
                  duration: int = 60, method: str = 'GET', 
                  data: Dict = None) -> List[PerformanceResult]:
        """Test de carga con múltiples usuarios concurrentes"""
        self.logger.info(f"🚀 Iniciando test de carga: {endpoint}")
        self.logger.info(f"👥 Usuarios concurrentes: {concurrent_users}")
        self.logger.info(f"⏱️  Duración: {duration} segundos")
        
        results = []
        start_time = time.time()
        
        def worker():
            """Worker para tests concurrentes"""
            worker_results = []
            while time.time() - start_time < duration:
                result = self.test_endpoint(endpoint, method, data)
                worker_results.append(result)
                time.sleep(0.1)  # Pequeña pausa entre requests
            return worker_results
        
        # Ejecutar tests concurrentes
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(worker) for _ in range(concurrent_users)]
            
            for future in as_completed(futures):
                try:
                    worker_results = future.result()
                    results.extend(worker_results)
                except Exception as e:
                    self.logger.error(f"❌ Error en worker: {e}")
        
        self.logger.info(f"✅ Test de carga completado: {len(results)} requests")
        return results
    
    def stress_test(self, endpoints: List[str], max_users: int = 100, 
                   step: int = 10, step_duration: int = 30) -> Dict[str, Any]:
        """Test de stress incrementando usuarios gradualmente"""
        self.logger.info("🔥 Iniciando test de stress")
        
        stress_results = {}
        
        for current_users in range(step, max_users + 1, step):
            self.logger.info(f"📈 Probando con {current_users} usuarios concurrentes")
            
            step_results = {}
            for endpoint in endpoints:
                results = self.load_test(
                    endpoint=endpoint,
                    concurrent_users=current_users,
                    duration=step_duration
                )
                
                # Calcular métricas
                response_times = [r.response_time for r in results if r.success]
                success_rate = sum(1 for r in results if r.success) / len(results) * 100
                
                step_results[endpoint] = {
                    'total_requests': len(results),
                    'successful_requests': sum(1 for r in results if r.success),
                    'failed_requests': sum(1 for r in results if not r.success),
                    'success_rate': success_rate,
                    'avg_response_time': statistics.mean(response_times) if response_times else 0,
                    'min_response_time': min(response_times) if response_times else 0,
                    'max_response_time': max(response_times) if response_times else 0,
                    'p95_response_time': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
                    'p99_response_time': statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0
                }
            
            stress_results[current_users] = step_results
            
            # Verificar si el sistema está fallando
            overall_success_rate = statistics.mean([
                step_results[ep]['success_rate'] for ep in endpoints
            ])
            
            if overall_success_rate < 50:
                self.logger.warning(f"⚠️  Success rate bajo ({overall_success_rate:.1f}%) con {current_users} usuarios")
                break
        
        return stress_results
    
    def benchmark_endpoints(self, endpoints: List[str], iterations: int = 100) -> Dict[str, Any]:
        """Benchmark de endpoints individuales"""
        self.logger.info("📊 Iniciando benchmark de endpoints")
        
        benchmark_results = {}
        
        for endpoint in endpoints:
            self.logger.info(f"🎯 Benchmarking: {endpoint}")
            
            results = []
            for i in range(iterations):
                result = self.test_endpoint(endpoint)
                results.append(result)
                
                if (i + 1) % 10 == 0:
                    self.logger.info(f"  Progreso: {i + 1}/{iterations}")
            
            # Calcular estadísticas
            response_times = [r.response_time for r in results if r.success]
            success_rate = sum(1 for r in results if r.success) / len(results) * 100
            
            benchmark_results[endpoint] = {
                'total_requests': len(results),
                'successful_requests': sum(1 for r in results if r.success),
                'success_rate': success_rate,
                'avg_response_time': statistics.mean(response_times) if response_times else 0,
                'median_response_time': statistics.median(response_times) if response_times else 0,
                'min_response_time': min(response_times) if response_times else 0,
                'max_response_time': max(response_times) if response_times else 0,
                'std_response_time': statistics.stdev(response_times) if len(response_times) > 1 else 0,
                'p95_response_time': statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
                'p99_response_time': statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0
            }
        
        return benchmark_results
    
    async def async_load_test(self, endpoint: str, concurrent_users: int = 50, 
                             total_requests: int = 1000) -> List[PerformanceResult]:
        """Test de carga asíncrono para mayor concurrencia"""
        self.logger.info(f"🚀 Test de carga asíncrono: {endpoint}")
        self.logger.info(f"👥 Usuarios concurrentes: {concurrent_users}")
        self.logger.info(f"📊 Total requests: {total_requests}")
        
        url = f"{self.base_url}{endpoint}"
        results = []
        
        async def make_request(session, semaphore):
            """Hacer un request asíncrono"""
            async with semaphore:
                start_time = time.time()
                try:
                    async with session.get(url) as response:
                        await response.text()
                        end_time = time.time()
                        response_time = (end_time - start_time) * 1000
                        
                        return PerformanceResult(
                            endpoint=endpoint,
                            method='GET',
                            response_time=response_time,
                            status_code=response.status,
                            success=response.status < 400
                        )
                except Exception as e:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    return PerformanceResult(
                        endpoint=endpoint,
                        method='GET',
                        response_time=response_time,
                        status_code=0,
                        success=False,
                        error=str(e)
                    )
        
        # Ejecutar requests asíncronos
        semaphore = asyncio.Semaphore(concurrent_users)
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                make_request(session, semaphore) 
                for _ in range(total_requests)
            ]
            
            results = await asyncio.gather(*tasks)
        
        self.logger.info(f"✅ Test asíncrono completado: {len(results)} requests")
        return results
    
    def database_performance_test(self) -> Dict[str, Any]:
        """Test de performance de base de datos"""
        self.logger.info("🗄️  Iniciando test de performance de base de datos")
        
        db_endpoints = [
            '/api/v1/stats/business',
            '/api/v1/search/products',
            '/api/v1/search/sales',
            '/api/v1/search/users',
            '/api/v1/reports/sales/summary',
            '/api/v1/reports/inventory/status'
        ]
        
        results = {}
        
        for endpoint in db_endpoints:
            self.logger.info(f"🎯 Testing DB endpoint: {endpoint}")
            
            # Test con diferentes cargas
            for load in [1, 5, 10, 20]:
                load_results = self.load_test(
                    endpoint=endpoint,
                    concurrent_users=load,
                    duration=30
                )
                
                response_times = [r.response_time for r in load_results if r.success]
                success_rate = sum(1 for r in load_results if r.success) / len(load_results) * 100
                
                if endpoint not in results:
                    results[endpoint] = {}
                
                results[endpoint][f'{load}_users'] = {
                    'avg_response_time': statistics.mean(response_times) if response_times else 0,
                    'success_rate': success_rate,
                    'total_requests': len(load_results)
                }
        
        return results
    
    def memory_leak_test(self, endpoint: str, duration: int = 300) -> Dict[str, Any]:
        """Test para detectar memory leaks"""
        self.logger.info(f"🧠 Test de memory leak: {endpoint}")
        
        import psutil
        process = psutil.Process()
        
        memory_usage = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            # Hacer requests
            for _ in range(10):
                self.test_endpoint(endpoint)
            
            # Medir memoria
            memory_info = process.memory_info()
            memory_usage.append({
                'timestamp': time.time(),
                'rss': memory_info.rss,
                'vms': memory_info.vms
            })
            
            time.sleep(5)
        
        # Analizar tendencia de memoria
        rss_values = [m['rss'] for m in memory_usage]
        memory_trend = 'increasing' if rss_values[-1] > rss_values[0] * 1.1 else 'stable'
        
        return {
            'endpoint': endpoint,
            'duration': duration,
            'memory_samples': len(memory_usage),
            'initial_memory': rss_values[0],
            'final_memory': rss_values[-1],
            'max_memory': max(rss_values),
            'avg_memory': statistics.mean(rss_values),
            'memory_trend': memory_trend,
            'potential_leak': memory_trend == 'increasing'
        }
    
    def generate_report(self, results: Dict[str, Any], output_file: str = None) -> str:
        """Generar reporte de performance"""
        report = {
            'test_summary': {
                'timestamp': datetime.now().isoformat(),
                'base_url': self.base_url,
                'total_tests': len(results)
            },
            'results': results,
            'recommendations': []
        }
        
        # Analizar resultados y generar recomendaciones
        for test_name, test_results in results.items():
            if 'avg_response_time' in test_results:
                avg_time = test_results['avg_response_time']
                
                if avg_time > 2000:
                    report['recommendations'].append(
                        f"⚠️  {test_name}: Tiempo de respuesta alto ({avg_time:.0f}ms). Considerar optimización."
                    )
                elif avg_time > 1000:
                    report['recommendations'].append(
                        f"⚠️  {test_name}: Tiempo de respuesta moderado ({avg_time:.0f}ms). Monitorear."
                    )
                else:
                    report['recommendations'].append(
                        f"✅ {test_name}: Tiempo de respuesta aceptable ({avg_time:.0f}ms)."
                    )
        
        # Guardar reporte
        report_json = json.dumps(report, indent=2, ensure_ascii=False)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_json)
            self.logger.info(f"📄 Reporte guardado en: {output_file}")
        
        return report_json
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Ejecutar suite completa de tests de performance"""
        self.logger.info("🚀 Iniciando suite completa de tests de performance")
        self.logger.info("=" * 60)
        
        # Endpoints críticos para testear
        critical_endpoints = [
            '/health',
            '/api/v1/stats/system',
            '/api/v1/stats/business',
            '/api/v1/stats/performance',
            '/api/v1/search/products',
            '/api/v1/search/sales',
            '/api/v1/reports/sales/summary'
        ]
        
        all_results = {}
        
        # 1. Benchmark de endpoints individuales
        self.logger.info("📊 1. Benchmark de endpoints individuales")
        benchmark_results = self.benchmark_endpoints(critical_endpoints, iterations=50)
        all_results['benchmark'] = benchmark_results
        
        # 2. Test de carga ligera
        self.logger.info("⚡ 2. Test de carga ligera")
        light_load_results = {}
        for endpoint in critical_endpoints[:3]:  # Solo los más críticos
            results = self.load_test(endpoint, concurrent_users=5, duration=30)
            response_times = [r.response_time for r in results if r.success]
            success_rate = sum(1 for r in results if r.success) / len(results) * 100
            
            light_load_results[endpoint] = {
                'avg_response_time': statistics.mean(response_times) if response_times else 0,
                'success_rate': success_rate,
                'total_requests': len(results)
            }
        
        all_results['light_load'] = light_load_results
        
        # 3. Test de carga media
        self.logger.info("🔋 3. Test de carga media")
        medium_load_results = {}
        for endpoint in critical_endpoints[:2]:  # Solo los más críticos
            results = self.load_test(endpoint, concurrent_users=10, duration=30)
            response_times = [r.response_time for r in results if r.success]
            success_rate = sum(1 for r in results if r.success) / len(results) * 100
            
            medium_load_results[endpoint] = {
                'avg_response_time': statistics.mean(response_times) if response_times else 0,
                'success_rate': success_rate,
                'total_requests': len(results)
            }
        
        all_results['medium_load'] = medium_load_results
        
        # 4. Test de stress
        self.logger.info("🔥 4. Test de stress")
        stress_results = self.stress_test(critical_endpoints[:2], max_users=30, step=5, step_duration=20)
        all_results['stress'] = stress_results
        
        # 5. Test de memory leak
        self.logger.info("🧠 5. Test de memory leak")
        memory_results = {}
        for endpoint in critical_endpoints[:2]:
            memory_result = self.memory_leak_test(endpoint, duration=60)
            memory_results[endpoint] = memory_result
        
        all_results['memory_leak'] = memory_results
        
        # 6. Test de base de datos
        self.logger.info("🗄️  6. Test de performance de base de datos")
        db_results = self.database_performance_test()
        all_results['database_performance'] = db_results
        
        self.logger.info("✅ Suite completa de tests completada")
        return all_results


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Tests de Performance para O'Data POS v2.0.0"
    )
    
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='URL base del servidor (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--test-type',
        choices=['benchmark', 'load', 'stress', 'memory', 'database', 'comprehensive'],
        default='comprehensive',
        help='Tipo de test a ejecutar'
    )
    
    parser.add_argument(
        '--endpoint',
        default='/health',
        help='Endpoint específico para testear'
    )
    
    parser.add_argument(
        '--users',
        type=int,
        default=10,
        help='Número de usuarios concurrentes'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Duración del test en segundos'
    )
    
    parser.add_argument(
        '--output',
        help='Archivo de salida para el reporte'
    )
    
    args = parser.parse_args()
    
    # Crear tester
    tester = PerformanceTester(args.url)
    
    # Ejecutar test según el tipo
    if args.test_type == 'benchmark':
        results = tester.benchmark_endpoints([args.endpoint])
    elif args.test_type == 'load':
        load_results = tester.load_test(args.endpoint, args.users, args.duration)
        response_times = [r.response_time for r in load_results if r.success]
        success_rate = sum(1 for r in load_results if r.success) / len(load_results) * 100
        results = {
            'load_test': {
                'endpoint': args.endpoint,
                'avg_response_time': statistics.mean(response_times) if response_times else 0,
                'success_rate': success_rate,
                'total_requests': len(load_results)
            }
        }
    elif args.test_type == 'stress':
        results = {'stress_test': tester.stress_test([args.endpoint])}
    elif args.test_type == 'memory':
        results = {'memory_test': tester.memory_leak_test(args.endpoint)}
    elif args.test_type == 'database':
        results = {'database_test': tester.database_performance_test()}
    else:  # comprehensive
        results = tester.run_comprehensive_test()
    
    # Generar reporte
    output_file = args.output or f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report = tester.generate_report(results, output_file)
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PERFORMANCE")
    print("=" * 60)
    
    if 'benchmark' in results:
        print("\n🎯 BENCHMARK RESULTS:")
        for endpoint, metrics in results['benchmark'].items():
            print(f"  {endpoint}:")
            print(f"    Tiempo promedio: {metrics['avg_response_time']:.2f}ms")
            print(f"    Success rate: {metrics['success_rate']:.1f}%")
    
    if 'stress' in results:
        print("\n🔥 STRESS TEST RESULTS:")
        max_users = max(results['stress'].keys())
        print(f"  Máximo usuarios soportados: {max_users}")
    
    print(f"\n📄 Reporte completo guardado en: {output_file}")
    print("✅ Tests de performance completados!")


if __name__ == "__main__":
    main()
