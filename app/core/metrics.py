"""
Sistema de Métricas y Monitoreo Empresarial
Instrumentación avanzada para observabilidad y performance
"""

import time
import logging
import threading
from typing import Dict, Any, Optional, List, Callable
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps
from flask import request, g, current_app
from dataclasses import dataclass, field
import psutil
import os

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Punto de métrica con timestamp"""
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class MetricSummary:
    """Resumen estadístico de métricas"""
    count: int
    sum: float
    min: float
    max: float
    avg: float
    p95: float
    p99: float

class MetricsCollector:
    """Colector central de métricas"""
    
    def __init__(self, max_points: int = 10000):
        self.max_points = max_points
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
        
        # Métricas de sistema
        self._system_metrics_enabled = True
        self._last_system_check = datetime.utcnow()
        
    def counter(self, name: str, value: int = 1, labels: Dict[str, str] = None) -> None:
        """Incrementar contador"""
        key = self._build_key(name, labels)
        with self._lock:
            self._counters[key] += value
            self._add_metric_point(name, self._counters[key], labels)
    
    def gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Establecer valor de gauge"""
        key = self._build_key(name, labels)
        with self._lock:
            self._gauges[key] = value
            self._add_metric_point(name, value, labels)
    
    def histogram(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Agregar valor a histograma"""
        key = self._build_key(name, labels)
        with self._lock:
            self._histograms[key].append(value)
            # Mantener solo los últimos 1000 valores
            if len(self._histograms[key]) > 1000:
                self._histograms[key] = self._histograms[key][-1000:]
            self._add_metric_point(name, value, labels)
    
    def timer(self, name: str, labels: Dict[str, str] = None):
        """Context manager para medir tiempo"""
        return MetricTimer(self, name, labels)
    
    def _build_key(self, name: str, labels: Dict[str, str] = None) -> str:
        """Construir clave única para métrica"""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}[{label_str}]"
    
    def _add_metric_point(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """Agregar punto de métrica"""
        point = MetricPoint(value=value, timestamp=datetime.utcnow(), labels=labels or {})
        self._metrics[name].append(point)
    
    def get_metric_summary(self, name: str, since: datetime = None) -> Optional[MetricSummary]:
        """Obtener resumen estadístico de métrica"""
        if name not in self._metrics:
            return None
        
        points = list(self._metrics[name])
        if since:
            points = [p for p in points if p.timestamp >= since]
        
        if not points:
            return None
        
        values = [p.value for p in points]
        values.sort()
        
        count = len(values)
        total = sum(values)
        min_val = min(values)
        max_val = max(values)
        avg = total / count
        
        # Percentiles
        p95_idx = int(count * 0.95)
        p99_idx = int(count * 0.99)
        p95 = values[p95_idx] if p95_idx < count else max_val
        p99 = values[p99_idx] if p99_idx < count else max_val
        
        return MetricSummary(
            count=count,
            sum=total,
            min=min_val,
            max=max_val,
            avg=avg,
            p95=p95,
            p99=p99
        )
    
    def get_current_values(self) -> Dict[str, Any]:
        """Obtener valores actuales de todas las métricas"""
        with self._lock:
            return {
                'counters': dict(self._counters),
                'gauges': dict(self._gauges),
                'system': self._get_system_metrics() if self._system_metrics_enabled else {}
            }
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Obtener métricas del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'system_cpu_percent': cpu_percent,
                'system_memory_percent': memory.percent,
                'system_memory_available_mb': memory.available / 1024 / 1024,
                'system_disk_percent': disk.percent,
                'system_disk_free_gb': disk.free / 1024 / 1024 / 1024,
                'system_load_1m': os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0,
                'process_memory_mb': psutil.Process().memory_info().rss / 1024 / 1024,
                'process_cpu_percent': psutil.Process().cpu_percent()
            }
        except Exception as e:
            logger.warning(f"Error obteniendo métricas del sistema: {e}")
            return {}

class MetricTimer:
    """Context manager para medir tiempo de ejecución"""
    
    def __init__(self, collector: MetricsCollector, name: str, labels: Dict[str, str] = None):
        self.collector = collector
        self.name = name
        self.labels = labels
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.collector.histogram(self.name, duration, self.labels)

class ApplicationMetrics:
    """Métricas específicas de la aplicación POS"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Registrar métrica de request HTTP"""
        labels = {
            'method': method,
            'endpoint': endpoint or 'unknown',
            'status_code': str(status_code),
            'status_class': f"{status_code // 100}xx"
        }
        
        self.collector.counter('http_requests_total', 1, labels)
        self.collector.histogram('http_request_duration_seconds', duration, labels)
        
        # Métricas específicas por status
        if status_code >= 500:
            self.collector.counter('http_requests_errors_total', 1, labels)
        elif status_code >= 400:
            self.collector.counter('http_requests_client_errors_total', 1, labels)
    
    def record_database_operation(self, operation: str, table: str, duration: float, success: bool):
        """Registrar operación de base de datos"""
        labels = {
            'operation': operation,
            'table': table,
            'status': 'success' if success else 'error'
        }
        
        self.collector.counter('database_operations_total', 1, labels)
        self.collector.histogram('database_operation_duration_seconds', duration, labels)
    
    def record_business_event(self, event_type: str, entity_type: str):
        """Registrar evento de negocio"""
        labels = {
            'event_type': event_type,
            'entity_type': entity_type
        }
        
        self.collector.counter('business_events_total', 1, labels)
    
    def record_cache_operation(self, operation: str, hit: bool):
        """Registrar operación de cache"""
        labels = {
            'operation': operation,
            'result': 'hit' if hit else 'miss'
        }
        
        self.collector.counter('cache_operations_total', 1, labels)
    
    def record_authentication_attempt(self, success: bool, method: str = 'password'):
        """Registrar intento de autenticación"""
        labels = {
            'method': method,
            'result': 'success' if success else 'failure'
        }
        
        self.collector.counter('auth_attempts_total', 1, labels)
    
    def update_active_users(self, count: int):
        """Actualizar número de usuarios activos"""
        self.collector.gauge('active_users_current', count)
    
    def update_inventory_metrics(self, total_products: int, low_stock_count: int, out_of_stock_count: int):
        """Actualizar métricas de inventario"""
        self.collector.gauge('inventory_products_total', total_products)
        self.collector.gauge('inventory_low_stock_count', low_stock_count)
        self.collector.gauge('inventory_out_of_stock_count', out_of_stock_count)

class HealthChecker:
    """Verificador de salud del sistema"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.checks: Dict[str, Callable[[], bool]] = {}
    
    def register_check(self, name: str, check_func: Callable[[], bool]):
        """Registrar verificación de salud"""
        self.checks[name] = check_func
    
    def run_all_checks(self) -> Dict[str, Dict[str, Any]]:
        """Ejecutar todas las verificaciones"""
        results = {}
        overall_healthy = True
        
        for name, check_func in self.checks.items():
            start_time = time.time()
            try:
                is_healthy = check_func()
                duration = time.time() - start_time
                
                results[name] = {
                    'healthy': is_healthy,
                    'duration': duration,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                if not is_healthy:
                    overall_healthy = False
                
                # Registrar métricas
                self.collector.gauge(f'health_check_{name}', 1.0 if is_healthy else 0.0)
                self.collector.histogram(f'health_check_duration_{name}', duration)
                
            except Exception as e:
                duration = time.time() - start_time
                results[name] = {
                    'healthy': False,
                    'error': str(e),
                    'duration': duration,
                    'timestamp': datetime.utcnow().isoformat()
                }
                overall_healthy = False
                
                logger.error(f"Health check {name} failed: {e}")
                self.collector.gauge(f'health_check_{name}', 0.0)
        
        results['overall'] = {
            'healthy': overall_healthy,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return results

# Instancia global
metrics_collector = MetricsCollector()
app_metrics = ApplicationMetrics(metrics_collector)
health_checker = HealthChecker(metrics_collector)

def setup_metrics(app):
    """Configurar sistema de métricas para la aplicación"""
    
    # Registrar verificaciones de salud básicas
    def check_database():
        """Verificar conexión a base de datos"""
        try:
            from app.core.database import db
            db.session.execute('SELECT 1')
            return True
        except Exception:
            return False
    
    def check_redis():
        """Verificar conexión a Redis"""
        try:
            if hasattr(app, 'redis'):
                app.redis.ping()
                return True
            return False
        except Exception:
            return False
    
    health_checker.register_check('database', check_database)
    health_checker.register_check('redis', check_redis)
    
    # Middleware para métricas de requests
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = f"{int(time.time())}-{threading.get_ident()}"
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            g.request_duration = duration
            
            app_metrics.record_request(
                method=request.method,
                endpoint=request.endpoint,
                status_code=response.status_code,
                duration=duration
            )
        
        return response
    
    app.logger.info("Sistema de métricas configurado")

# Decoradores para instrumentación
def track_execution_time(metric_name: str, labels: Dict[str, str] = None):
    """Decorador para medir tiempo de ejecución"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with metrics_collector.timer(metric_name, labels):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def count_calls(metric_name: str, labels: Dict[str, str] = None):
    """Decorador para contar llamadas a función"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                metrics_collector.counter(metric_name, 1, {**(labels or {}), 'status': 'success'})
                return result
            except Exception as e:
                metrics_collector.counter(metric_name, 1, {**(labels or {}), 'status': 'error'})
                raise
        return wrapper
    return decorator

def track_business_event(event_type: str, entity_type: str):
    """Decorador para rastrear eventos de negocio"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            app_metrics.record_business_event(event_type, entity_type)
            return result
        return wrapper
    return decorator

# Endpoints de métricas
def register_metrics_endpoints(app):
    """Registrar endpoints para exponer métricas"""
    
    @app.route('/metrics')
    def metrics_endpoint():
        """Endpoint para métricas en formato Prometheus"""
        from flask import Response
        
        try:
            metrics_data = metrics_collector.get_current_values()
            
            # Formato simple para métricas (en producción usar prometheus_client)
            output = []
            
            # Contadores
            for name, value in metrics_data['counters'].items():
                output.append(f'# TYPE {name} counter')
                output.append(f'{name} {value}')
            
            # Gauges
            for name, value in metrics_data['gauges'].items():
                output.append(f'# TYPE {name} gauge')
                output.append(f'{name} {value}')
            
            # Métricas del sistema
            for name, value in metrics_data['system'].items():
                output.append(f'# TYPE {name} gauge')
                output.append(f'{name} {value}')
            
            return Response('\n'.join(output), mimetype='text/plain')
            
        except Exception as e:
            logger.error(f"Error generando métricas: {e}")
            return {'error': 'Error interno'}, 500
    
    @app.route('/health')
    def health_endpoint():
        """Endpoint de health check detallado"""
        try:
            health_results = health_checker.run_all_checks()
            status_code = 200 if health_results['overall']['healthy'] else 503
            
            return health_results, status_code
            
        except Exception as e:
            logger.error(f"Error en health check: {e}")
            return {
                'overall': {'healthy': False},
                'error': str(e)
            }, 500
