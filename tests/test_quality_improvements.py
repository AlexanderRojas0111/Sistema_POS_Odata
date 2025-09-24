"""
Tests para Validar Mejoras de Calidad Empresariales
Suite completa de testing para las mejoras implementadas
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
from app import create_app
from app.core.database import db
from app.core.exceptions import ValidationException, AuthenticationException
from app.core.validators import SecurityValidator, BaseValidator
from app.core.metrics import metrics_collector, app_metrics

@pytest.fixture
def app():
    """Aplicación de prueba con configuración de testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de prueba"""
    return app.test_client()

class TestSecurityValidation:
    """Tests para validación de seguridad"""
    
    def test_sql_injection_detection(self):
        """Test: Detección de inyección SQL"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "admin' OR '1'='1",
            "UNION SELECT * FROM passwords",
            "1; DELETE FROM products"
        ]
        
        for malicious_input in malicious_inputs:
            assert SecurityValidator.check_sql_injection(malicious_input)
    
    def test_xss_detection(self):
        """Test: Detección de XSS"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<iframe src='malicious.com'></iframe>",
            "<img onerror='alert(1)' src='x'>"
        ]
        
        for malicious_input in malicious_inputs:
            assert SecurityValidator.check_xss(malicious_input)
    
    def test_safe_input_validation(self):
        """Test: Validación de entrada segura"""
        # Entrada segura
        safe_input = "Producto normal 123"
        result = SecurityValidator.validate_safe_input(safe_input, 'test_field')
        assert result == safe_input
        
        # Entrada maliciosa
        with pytest.raises(ValidationException):
            SecurityValidator.validate_safe_input("'; DROP TABLE users; --", 'test_field')
    
    def test_string_sanitization(self):
        """Test: Sanitización de strings"""
        test_cases = [
            ("  Texto con espacios  ", "Texto con espacios"),
            ("Texto\n\ncon\t\ttabs", "Texto con tabs"),
            ("Texto<script>alert()</script>", "Textalert()"),
            ("'Texto' con \"comillas\"", "Texto con comillas")
        ]
        
        for input_str, expected in test_cases:
            result = BaseValidator.sanitize_string(input_str)
            assert result == expected

class TestExceptionHandling:
    """Tests para manejo de excepciones"""
    
    def test_validation_exception_structure(self):
        """Test: Estructura de excepción de validación"""
        exception = ValidationException(
            message="Test error",
            field="test_field",
            value="invalid_value"
        )
        
        error_dict = exception.to_dict()
        
        assert error_dict['success'] is False
        assert error_dict['error']['code'] == 'VALIDATION_ERROR'
        assert error_dict['error']['details']['field'] == 'test_field'
        assert 'timestamp' in error_dict['error']
    
    def test_authentication_exception(self):
        """Test: Excepción de autenticación"""
        exception = AuthenticationException("Invalid credentials")
        
        assert exception.status_code == 401
        assert exception.error_code == 'AUTHENTICATION_ERROR'
        assert "Credenciales" in exception.user_message
    
    def test_exception_handler_integration(self, client):
        """Test: Integración de manejadores de excepción"""
        # Simular endpoint que lanza excepción
        with client.application.test_request_context():
            from app.core.exceptions import handle_pos_exception
            
            exception = ValidationException("Test validation error")
            response = handle_pos_exception(exception)
            
            assert response[1] == 400  # Status code
            data = json.loads(response[0].data)
            assert data['success'] is False
            assert data['error']['code'] == 'VALIDATION_ERROR'

class TestMetricsSystem:
    """Tests para sistema de métricas"""
    
    def test_counter_increment(self):
        """Test: Incremento de contador"""
        initial_value = metrics_collector._counters.get('test_counter', 0)
        metrics_collector.counter('test_counter', 5)
        
        assert metrics_collector._counters['test_counter'] == initial_value + 5
    
    def test_gauge_setting(self):
        """Test: Configuración de gauge"""
        metrics_collector.gauge('test_gauge', 42.5)
        
        assert metrics_collector._gauges['test_gauge'] == 42.5
    
    def test_histogram_values(self):
        """Test: Valores de histograma"""
        test_values = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        for value in test_values:
            metrics_collector.histogram('test_histogram', value)
        
        summary = metrics_collector.get_metric_summary('test_histogram')
        
        assert summary.count == len(test_values)
        assert summary.avg == 3.0
        assert summary.min == 1.0
        assert summary.max == 5.0
    
    def test_timer_context_manager(self):
        """Test: Context manager de timer"""
        with metrics_collector.timer('test_timer'):
            time.sleep(0.01)  # 10ms
        
        summary = metrics_collector.get_metric_summary('test_timer')
        assert summary.count == 1
        assert summary.avg >= 0.01

class TestApplicationMetrics:
    """Tests para métricas de aplicación"""
    
    def test_request_metrics(self):
        """Test: Métricas de request HTTP"""
        app_metrics.record_request('GET', '/api/v1/products', 200, 0.15)
        
        # Verificar que se registraron las métricas
        counters = metrics_collector._counters
        assert any('http_requests_total' in key for key in counters.keys())
    
    def test_database_metrics(self):
        """Test: Métricas de base de datos"""
        app_metrics.record_database_operation('SELECT', 'products', 0.05, True)
        
        counters = metrics_collector._counters
        assert any('database_operations_total' in key for key in counters.keys())
    
    def test_authentication_metrics(self):
        """Test: Métricas de autenticación"""
        app_metrics.record_authentication_attempt(True)
        app_metrics.record_authentication_attempt(False)
        
        counters = metrics_collector._counters
        success_metrics = [k for k in counters.keys() if 'auth_attempts_total' in k and 'success' in k]
        failure_metrics = [k for k in counters.keys() if 'auth_attempts_total' in k and 'failure' in k]
        
        assert len(success_metrics) > 0
        assert len(failure_metrics) > 0

class TestHealthChecks:
    """Tests para verificaciones de salud"""
    
    def test_health_check_registration(self):
        """Test: Registro de verificaciones de salud"""
        from app.core.metrics import health_checker
        
        def dummy_check():
            return True
        
        health_checker.register_check('dummy', dummy_check)
        assert 'dummy' in health_checker.checks
    
    def test_health_check_execution(self):
        """Test: Ejecución de verificaciones"""
        from app.core.metrics import health_checker
        
        def passing_check():
            return True
        
        def failing_check():
            return False
        
        health_checker.register_check('passing', passing_check)
        health_checker.register_check('failing', failing_check)
        
        results = health_checker.run_all_checks()
        
        assert results['passing']['healthy'] is True
        assert results['failing']['healthy'] is False
        assert results['overall']['healthy'] is False

class TestSecurityMiddleware:
    """Tests para middleware de seguridad"""
    
    def test_security_headers(self, client):
        """Test: Headers de seguridad"""
        response = client.get('/health')
        
        # Verificar headers de seguridad
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
    
    def test_request_id_generation(self, client):
        """Test: Generación de ID de request"""
        response = client.get('/health')
        
        assert 'X-Request-ID' in response.headers
        assert len(response.headers['X-Request-ID']) > 0
    
    def test_suspicious_url_blocking(self, client):
        """Test: Bloqueo de URLs sospechosas"""
        suspicious_urls = [
            '/admin',
            '/phpmyadmin',
            '/.env',
            '/wp-admin'
        ]
        
        for url in suspicious_urls:
            response = client.get(url)
            assert response.status_code == 404

class TestLoggingSystem:
    """Tests para sistema de logging"""
    
    def test_context_filter(self, app):
        """Test: Filtro de contexto en logs"""
        from app.core.logging_config import ContextFilter
        
        context_filter = ContextFilter()
        
        # Crear record de prueba
        import logging
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=1,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        with app.test_request_context('/test'):
            result = context_filter.filter(record)
            
            assert result is True
            assert hasattr(record, 'request_id')
            assert hasattr(record, 'endpoint')
            assert hasattr(record, 'method')
    
    def test_security_filter(self):
        """Test: Filtro de eventos de seguridad"""
        from app.core.logging_config import SecurityFilter
        
        security_filter = SecurityFilter()
        
        # Record con contenido de seguridad
        import logging
        record = logging.LogRecord(
            name='test',
            level=logging.WARNING,
            pathname='test.py',
            lineno=1,
            msg='Authentication failed for user',
            args=(),
            exc_info=None
        )
        
        result = security_filter.filter(record)
        
        assert result is True
        assert record.is_security_event is True
        assert record.security_level == 'HIGH'

class TestIntegrationQuality:
    """Tests de integración para mejoras de calidad"""
    
    def test_complete_auth_flow_with_metrics(self, client):
        """Test: Flujo completo de autenticación con métricas"""
        # Login
        response = client.post('/api/v1/auth/login',
                              json={'username': 'admin', 'password': 'admin'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verificar estructura de respuesta mejorada
        assert data['success'] is True
        assert 'data' in data
        assert 'access_token' in data['data']
        assert 'expires_in' in data['data']
        
        # Verificar que se registraron métricas
        counters = metrics_collector._counters
        auth_metrics = [k for k in counters.keys() if 'auth_attempts_total' in k]
        assert len(auth_metrics) > 0
    
    def test_health_endpoint_with_metrics(self, client):
        """Test: Endpoint de health con métricas"""
        response = client.get('/health')
        
        assert response.status_code in [200, 503]  # Puede ser unhealthy pero debe responder
        data = json.loads(response.data)
        
        # Verificar estructura de health check mejorada
        assert 'overall' in data
        assert 'timestamp' in data['overall']
    
    def test_metrics_endpoint(self, client):
        """Test: Endpoint de métricas"""
        # Generar algunas métricas primero
        client.get('/health')
        client.get('/ai-test')
        
        response = client.get('/metrics')
        
        assert response.status_code == 200
        assert response.content_type == 'text/plain; charset=utf-8'
        
        # Verificar formato de métricas
        content = response.data.decode('utf-8')
        assert 'TYPE' in content  # Formato Prometheus
    
    def test_error_handling_integration(self, client):
        """Test: Integración de manejo de errores"""
        # Request con datos inválidos
        response = client.post('/api/v1/auth/login',
                              json={'username': '', 'password': ''})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        # Verificar estructura de error estandarizada
        assert data['success'] is False
        assert 'error' in data
        assert 'code' in data['error']
        assert 'timestamp' in data['error']
    
    def test_security_headers_integration(self, client):
        """Test: Integración de headers de seguridad"""
        response = client.get('/health')
        
        # Verificar todos los headers de seguridad
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Content-Security-Policy',
            'X-Request-ID'
        ]
        
        for header in security_headers:
            assert header in response.headers
    
    @patch('app.core.metrics.psutil.cpu_percent')
    @patch('app.core.metrics.psutil.virtual_memory')
    def test_system_metrics_collection(self, mock_memory, mock_cpu, client):
        """Test: Recolección de métricas del sistema"""
        # Mock de métricas del sistema
        mock_cpu.return_value = 25.5
        mock_memory.return_value = MagicMock(percent=60.0, available=1024*1024*1024)
        
        # Obtener métricas actuales
        current_metrics = metrics_collector.get_current_values()
        
        assert 'system' in current_metrics
        system_metrics = current_metrics['system']
        
        if system_metrics:  # Solo si las métricas del sistema están habilitadas
            assert 'system_cpu_percent' in system_metrics
            assert 'system_memory_percent' in system_metrics

class TestPerformanceOptimizations:
    """Tests para optimizaciones de rendimiento"""
    
    def test_execution_time_tracking(self):
        """Test: Seguimiento de tiempo de ejecución"""
        from app.core.metrics import track_execution_time
        
        @track_execution_time('test_function_duration')
        def test_function():
            time.sleep(0.01)
            return "result"
        
        result = test_function()
        
        assert result == "result"
        
        # Verificar que se registró la métrica
        summary = metrics_collector.get_metric_summary('test_function_duration')
        assert summary is not None
        assert summary.count == 1
    
    def test_call_counting(self):
        """Test: Conteo de llamadas a función"""
        from app.core.metrics import count_calls
        
        @count_calls('test_function_calls')
        def test_function():
            return "result"
        
        # Llamar función varias veces
        for _ in range(3):
            test_function()
        
        # Verificar conteo
        counters = metrics_collector._counters
        success_counter = [v for k, v in counters.items() 
                          if 'test_function_calls' in k and 'success' in k]
        assert len(success_counter) > 0
        assert success_counter[0] == 3

class TestBusinessLogicValidation:
    """Tests para validación de lógica de negocio"""
    
    def test_sale_validation_schema(self):
        """Test: Validación de esquema de venta"""
        from app.core.validators import SaleValidationSchema
        
        valid_sale = {
            'items': [
                {
                    'product_id': 1,
                    'quantity': 2,
                    'unit_price': '10.50'
                }
            ],
            'payment_method': 'cash',
            'discount_amount': '0.00',
            'tax_amount': '2.10'
        }
        
        schema = SaleValidationSchema()
        result = schema.load(valid_sale)
        
        assert result['items'][0]['quantity'] == 2
        assert result['payment_method'] == 'cash'
    
    def test_product_validation_schema(self):
        """Test: Validación de esquema de producto"""
        from app.core.validators import ProductValidationSchema
        
        valid_product = {
            'name': 'Producto Test',
            'sku': 'TEST-001',
            'price': '25.99',
            'min_stock': 5,
            'max_stock': 100
        }
        
        schema = ProductValidationSchema()
        result = schema.load(valid_product)
        
        assert result['name'] == 'Producto Test'
        assert result['sku'] == 'TEST-001'
        assert result['min_stock'] == 5

class TestQualityMetrics:
    """Tests para métricas de calidad"""
    
    def test_code_coverage_tracking(self):
        """Test: Seguimiento de cobertura de código"""
        # Este test verifica que el sistema de métricas esté funcionando
        # La cobertura real se mide con pytest-cov
        
        # Simular ejecución de código instrumentado
        with metrics_collector.timer('code_execution'):
            time.sleep(0.001)
        
        summary = metrics_collector.get_metric_summary('code_execution')
        assert summary is not None
        assert summary.count == 1
    
    def test_error_rate_calculation(self):
        """Test: Cálculo de tasa de errores"""
        # Simular requests exitosos y fallidos
        for _ in range(7):
            app_metrics.record_request('GET', '/api/test', 200, 0.1)
        
        for _ in range(3):
            app_metrics.record_request('GET', '/api/test', 500, 0.2)
        
        # Verificar métricas
        counters = metrics_collector._counters
        
        # Buscar métricas de requests
        total_requests = sum(v for k, v in counters.items() if 'http_requests_total' in k)
        error_requests = sum(v for k, v in counters.items() if 'http_requests_errors_total' in k)
        
        assert total_requests >= 10
        assert error_requests >= 3

class TestSystemRobustness:
    """Tests para robustez del sistema"""
    
    def test_graceful_degradation(self, client):
        """Test: Degradación elegante del sistema"""
        # Simular fallo de Redis
        with patch('app.redis.ping', side_effect=Exception("Redis down")):
            response = client.get('/health')
            
            # El sistema debe seguir funcionando aunque Redis falle
            assert response.status_code in [200, 503]
    
    def test_input_size_limits(self, client):
        """Test: Límites de tamaño de entrada"""
        # Payload muy grande
        large_payload = {'data': 'x' * 10000}
        
        response = client.post('/api/v1/auth/login',
                              json=large_payload)
        
        # Debe manejar gracefully payloads grandes
        assert response.status_code in [400, 413, 422]
    
    def test_concurrent_request_handling(self, client):
        """Test: Manejo de requests concurrentes"""
        import threading
        
        results = []
        
        def make_request():
            response = client.get('/health')
            results.append(response.status_code)
        
        # Simular requests concurrentes
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Esperar a que terminen
        for thread in threads:
            thread.join()
        
        # Verificar que todos los requests fueron manejados
        assert len(results) == 5
        assert all(status in [200, 503] for status in results)
