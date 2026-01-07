"""
Sistema de Métricas - Sistema POS O'Data
=======================================
Métricas básicas para monitoreo del sistema
"""

import time
import logging
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from flask import request, g, current_app  # type: ignore[import]
from app.monitoring.alerts import check_and_send_alerts  # type: ignore[import]
try:  # Resolver import para chequeo de base de datos
    from sqlalchemy import text  # type: ignore[import]
except ImportError:
    text = None  # type: ignore

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Recolector de métricas del sistema"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._metrics = defaultdict(int)
        self._response_times = deque(maxlen=1000)  # Últimos 1000 requests
        self._error_counts = defaultdict(int)
        self._active_requests = 0
        self._start_time = datetime.utcnow()
    
    def increment(self, metric_name, value=1):
        """Incrementar contador de métrica"""
        with self._lock:
            self._metrics[metric_name] += value
    
    def record_response_time(self, duration):
        """Registrar tiempo de respuesta"""
        with self._lock:
            self._response_times.append(duration)
    
    def record_error(self, error_type, status_code):
        """Registrar error"""
        with self._lock:
            self._error_counts[f"{error_type}_{status_code}"] += 1
    
    def get_metrics(self):
        """Obtener métricas actuales"""
        with self._lock:
            uptime = (datetime.utcnow() - self._start_time).total_seconds()
            
            # Calcular tiempo de respuesta promedio
            avg_response_time = 0
            if self._response_times:
                avg_response_time = sum(self._response_times) / len(self._response_times)
            
            # Calcular requests por minuto
            requests_per_minute = 0
            if uptime > 0:
                total_requests = sum(self._metrics.values())
                requests_per_minute = (total_requests / uptime) * 60
            
            # Calcular tasa de errores
            total_errors = sum(self._error_counts.values())
            error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
            
            metrics = {
                "uptime_seconds": uptime,
                "uptime_human": str(timedelta(seconds=int(uptime))),
                "total_requests": total_requests,
                "requests_per_minute": round(requests_per_minute, 2),
                "active_requests": self._active_requests,
                "average_response_time_ms": round(avg_response_time * 1000, 2),
                "error_counts": dict(self._error_counts),
                "error_rate": round(error_rate, 2),
                "metrics": dict(self._metrics),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Verificar alertas
            try:
                health_status = health_checker.run_health_checks()
                check_and_send_alerts(metrics, health_status)
            except Exception as e:
                logger.error(f"Error checking alerts: {e}")
            
            return metrics
    
    def start_request(self):
        """Marcar inicio de request"""
        with self._lock:
            self._active_requests += 1
    
    def end_request(self):
        """Marcar fin de request"""
        with self._lock:
            self._active_requests = max(0, self._active_requests - 1)

# Instancia global del recolector
metrics_collector = MetricsCollector()

def track_request_metrics(f):
    """Decorator para rastrear métricas de requests"""
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        metrics_collector.start_request()
        
        try:
            # Incrementar contador de requests
            endpoint = f"{request.method} {request.endpoint or request.path}"
            metrics_collector.increment(f"requests_{endpoint}")
            metrics_collector.increment("total_requests")
            
            # Ejecutar función
            response = f(*args, **kwargs)
            
            # Registrar tiempo de respuesta
            duration = time.time() - start_time
            metrics_collector.record_response_time(duration)
            
            return response
            
        except Exception as e:
            # Registrar error
            error_type = type(e).__name__
            status_code = getattr(e, 'status_code', 500)
            metrics_collector.record_error(error_type, status_code)
            metrics_collector.increment("total_errors")
            raise
            
        finally:
            metrics_collector.end_request()
    
    return decorated_function

def track_database_operation(operation_type):
    """Decorator para rastrear operaciones de base de datos"""
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = f(*args, **kwargs)
                metrics_collector.increment(f"db_operations_{operation_type}_success")
                return result
                
            except Exception as e:
                metrics_collector.increment(f"db_operations_{operation_type}_error")
                raise
                
            finally:
                duration = time.time() - start_time
                metrics_collector.record_response_time(duration)
        
        return decorated_function
    return decorator

def track_business_metric(metric_name):
    """Decorator para rastrear métricas de negocio"""
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                result = f(*args, **kwargs)
                metrics_collector.increment(f"business_{metric_name}")
                return result
                
            except Exception as e:
                metrics_collector.increment(f"business_{metric_name}_error")
                raise
        
        return decorated_function
    return decorator

class HealthChecker:
    """Verificador de salud del sistema"""
    
    def __init__(self):
        self._checks = {}
    
    def register_check(self, name, check_function):
        """Registrar verificación de salud"""
        self._checks[name] = check_function
    
    def run_health_checks(self):
        """Ejecutar todas las verificaciones de salud"""
        results = {}
        overall_healthy = True
        
        for name, check_function in self._checks.items():
            try:
                result = check_function()
                results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "details": result
                }
                if not result:
                    overall_healthy = False
                    
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "details": str(e)
                }
                overall_healthy = False
        
        return {
            "overall_status": "healthy" if overall_healthy else "unhealthy",
            "checks": results,
            "timestamp": datetime.utcnow().isoformat()
        }

# Instancia global del verificador de salud
health_checker = HealthChecker()

def check_database_health():
    """Verificar salud de la base de datos"""
    if text is None:
        logger.warning("sqlalchemy no disponible; health check de DB omitido")
        return False
    try:
        from app import db
        db.session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

def check_redis_health():
    """Verificar salud de Redis"""
    try:
        from app.config.redis_config import is_redis_available, get_redis_info
        return is_redis_available()
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return False

def check_disk_space():
    """Verificar espacio en disco"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_percent = (free / total) * 100
        return free_percent > 10  # Al menos 10% libre
    except Exception as e:
        logger.warning(f"Disk space check failed: {e}")
        return True  # Si no se puede verificar, asumir OK

def check_memory_usage():
    """Verificar uso de memoria"""
    try:
        import psutil  # type: ignore[import]
        memory = psutil.virtual_memory()
        return memory.percent < 90  # Menos del 90% de uso
    except ImportError:
        # psutil no disponible, asumir OK
        return True
    except Exception as e:
        logger.warning(f"Memory check failed: {e}")
        return True

# Registrar verificaciones de salud
health_checker.register_check("database", check_database_health)
health_checker.register_check("redis", check_redis_health)
health_checker.register_check("disk_space", check_disk_space)
health_checker.register_check("memory", check_memory_usage)

class MonitoringMiddleware:
    """Middleware de monitoreo para la aplicación"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar middleware de monitoreo"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Ejecutar antes de cada request"""
        g.start_time = time.time()
        metrics_collector.start_request()
    
    def after_request(self, response):
        """Ejecutar después de cada request"""
        duration = None
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            metrics_collector.record_response_time(duration)
        
        metrics_collector.end_request()
        
        # Agregar headers de métricas
        if duration is not None:
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        response.headers['X-Request-ID'] = request.headers.get('X-Request-ID', 'unknown')
        
        return response

# Instancia del middleware de monitoreo
monitoring_middleware = MonitoringMiddleware()
