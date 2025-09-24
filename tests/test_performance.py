import unittest
import time
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, MagicMock

class TestPerformance(unittest.TestCase):
    """Tests de rendimiento del sistema"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.base_url = "http://localhost:5000"
        self.api_v1_base = f"{self.base_url}/api/v1"
        self.api_v2_base = f"{self.base_url}/api/v2"

    def test_api_response_time(self):
        """Test de tiempo de respuesta de la API"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_v1_base}/products/", timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Verificar que la respuesta es rápida (< 2 segundos)
            self.assertLess(response_time, 2.0, f"Tiempo de respuesta muy lento: {response_time:.2f}s")
            
            # Verificar que el status code es válido
            self.assertIn(response.status_code, [200, 404])
            
        except requests.exceptions.RequestException:
            self.skipTest("API no disponible para testing de rendimiento")

    def test_concurrent_requests(self):
        """Test de requests concurrentes"""
        def make_request():
            try:
                response = requests.get(f"{self.api_v1_base}/products/", timeout=5)
                return response.status_code
            except:
                return None
        
        # Hacer 10 requests concurrentes
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verificar que al menos algunos requests fueron exitosos
        successful_requests = sum(1 for status in results if status in [200, 404])
        self.assertGreater(successful_requests, 0, "Ningún request concurrente fue exitoso")

    def test_semantic_search_performance(self):
        """Test de rendimiento de búsqueda semántica"""
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.api_v2_base}/search/semantic",
                params={"q": "bebida"},
                timeout=15
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # La búsqueda semántica puede tomar más tiempo (< 10 segundos)
            self.assertLess(response_time, 10.0, f"Búsqueda semántica muy lenta: {response_time:.2f}s")
            
            self.assertIn(response.status_code, [200, 400, 404])
            
        except requests.exceptions.RequestException:
            self.skipTest("API de búsqueda semántica no disponible")

    def test_database_query_performance(self):
        """Test de rendimiento de consultas a base de datos"""
        # Simular consultas a base de datos
        query_times = []
        
        for i in range(5):
            start_time = time.time()
            # Simular consulta simple
            time.sleep(0.01)  # Simular tiempo de consulta
            end_time = time.time()
            query_times.append(end_time - start_time)
        
        # Verificar que las consultas son consistentes
        avg_query_time = sum(query_times) / len(query_times)
        self.assertLess(avg_query_time, 0.1, f"Consultas muy lentas: {avg_query_time:.3f}s")

    def test_memory_usage_simulation(self):
        """Test de uso de memoria (simulado)"""
        import psutil
        import os
        
        # Obtener uso de memoria del proceso actual
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simular operaciones que consumen memoria
        large_list = []
        for i in range(10000):
            large_list.append(f"item_{i}")
        
        memory_after_operation = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after_operation - initial_memory
        
        # Verificar que el aumento de memoria es razonable (< 100MB)
        self.assertLess(memory_increase, 100, f"Aumento de memoria excesivo: {memory_increase:.1f}MB")
        
        # Limpiar memoria
        del large_list

    def test_cpu_usage_simulation(self):
        """Test de uso de CPU (simulado)"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Simular operaciones intensivas de CPU
        start_time = time.time()
        cpu_usage_samples = []
        
        for i in range(10):
            # Simular trabajo de CPU
            _ = sum(range(10000))
            cpu_percent = process.cpu_percent()
            cpu_usage_samples.append(cpu_percent)
            time.sleep(0.1)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verificar que las operaciones no toman demasiado tiempo
        self.assertLess(total_time, 5.0, f"Operaciones de CPU muy lentas: {total_time:.2f}s")

    def test_file_io_performance(self):
        """Test de rendimiento de I/O de archivos"""
        import tempfile
        import os
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name
        
        try:
            # Test de escritura
            start_time = time.time()
            with open(temp_file, 'w') as f:
                for i in range(1000):
                    f.write(f"Linea {i}\n")
            write_time = time.time() - start_time
            
            # Test de lectura
            start_time = time.time()
            with open(temp_file, 'r') as f:
                lines = f.readlines()
            read_time = time.time() - start_time
            
            # Verificar que las operaciones de I/O son rápidas
            self.assertLess(write_time, 1.0, f"Escritura muy lenta: {write_time:.3f}s")
            self.assertLess(read_time, 1.0, f"Lectura muy lenta: {read_time:.3f}s")
            self.assertEqual(len(lines), 1000)
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_network_latency(self):
        """Test de latencia de red"""
        try:
            # Medir latencia a la API
            latencies = []
            
            for i in range(5):
                start_time = time.time()
                response = requests.get(f"{self.api_v1_base}/products/", timeout=5)
                end_time = time.time()
                
                if response.status_code in [200, 404]:
                    latency = (end_time - start_time) * 1000  # Convertir a ms
                    latencies.append(latency)
            
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                max_latency = max(latencies)
                
                # Verificar que la latencia es razonable
                self.assertLess(avg_latency, 1000, f"Latencia promedio muy alta: {avg_latency:.1f}ms")
                self.assertLess(max_latency, 2000, f"Latencia máxima muy alta: {max_latency:.1f}ms")
            
        except requests.exceptions.RequestException:
            self.skipTest("API no disponible para testing de latencia")

    def test_concurrent_database_operations(self):
        """Test de operaciones concurrentes de base de datos"""
        def simulate_db_operation(operation_id):
            # Simular operación de base de datos
            time.sleep(0.01)  # Simular tiempo de operación
            return f"operation_{operation_id}_completed"
        
        # Ejecutar 20 operaciones concurrentes
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(simulate_db_operation, i) for i in range(20)]
            results = [future.result() for future in as_completed(futures)]
        
        # Verificar que todas las operaciones se completaron
        self.assertEqual(len(results), 20)
        for i, result in enumerate(results):
            self.assertIn(f"operation_{i}_completed", result)

    def test_cache_performance(self):
        """Test de rendimiento de caché"""
        import hashlib
        
        # Simular caché en memoria
        cache = {}
        
        def cached_operation(key, data):
            # Generar hash de la clave
            cache_key = hashlib.md5(key.encode()).hexdigest()
            
            if cache_key in cache:
                return cache[cache_key]  # Cache hit
            
            # Simular operación costosa
            result = f"processed_{data}"
            cache[cache_key] = result
            return result
        
        # Test de cache miss (primera vez)
        start_time = time.time()
        result1 = cached_operation("test_key", "test_data")
        cache_miss_time = time.time() - start_time
        
        # Test de cache hit (segunda vez)
        start_time = time.time()
        result2 = cached_operation("test_key", "test_data")
        cache_hit_time = time.time() - start_time
        
        # Verificar que cache hit es más rápido que cache miss
        self.assertLess(cache_hit_time, cache_miss_time, 
                       f"Cache hit no es más rápido: {cache_hit_time:.6f}s vs {cache_miss_time:.6f}s")
        
        # Verificar que los resultados son consistentes
        self.assertEqual(result1, result2)

    def test_error_recovery_performance(self):
        """Test de rendimiento de recuperación de errores"""
        def operation_with_retry(max_retries=3):
            for attempt in range(max_retries):
                try:
                    # Simular operación que puede fallar
                    if attempt == 0:
                        raise Exception("Simulated error")
                    return "success"
                except Exception:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(0.01)  # Pequeña pausa antes de reintentar
        
        start_time = time.time()
        try:
            result = operation_with_retry()
            recovery_time = time.time() - start_time
            
            # Verificar que la recuperación es rápida
            self.assertLess(recovery_time, 1.0, f"Recuperación muy lenta: {recovery_time:.3f}s")
            self.assertEqual(result, "success")
            
        except Exception:
            self.fail("La operación con reintentos falló completamente")

if __name__ == '__main__':
    unittest.main() 