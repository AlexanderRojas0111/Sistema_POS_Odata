#!/usr/bin/env python3
"""
Sistema de Monitoring de Producción - Sistema POS O'Data
========================================================
Monitoring avanzado para ambiente de producción
"""

import requests
import time
import json
import smtplib
from email.mime.text import MimeText
from datetime import datetime, timedelta
import logging
import os
import psutil
import subprocess
from typing import Dict, List, Tuple, Optional
import threading
import queue

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/production_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProductionMonitoring:
    """Sistema de monitoring avanzado para producción"""
    
    def __init__(self, base_url: str, alert_email: Optional[str] = None):
        self.base_url = base_url
        self.alert_email = alert_email
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.check_interval = 60  # segundos
        self.response_times = []
        self.error_count = 0
        self.total_checks = 0
        self.alert_queue = queue.Queue()
        self.monitoring_active = True
        
        # Configuración de alertas más estrictas para producción
        self.alert_thresholds = {
            'response_time_ms': 500,  # 500ms
            'error_rate_percent': 2.0,  # 2%
            'consecutive_failures': 2,
            'cpu_usage_percent': 80,
            'memory_usage_percent': 85,
            'disk_usage_percent': 90
        }
        
        # Métricas históricas
        self.metrics_history = []
        self.max_history = 1000  # Mantener últimos 1000 registros
        
        logger.info(f"Production monitoring iniciado para: {base_url}")
    
    def check_health(self) -> Tuple[bool, str, float]:
        """
        Verificar salud del sistema
        
        Returns:
            Tuple[bool, str, float]: (is_healthy, message, response_time_ms)
        """
        start_time = time.time()
        
        try:
            response = requests.get(
                f"{self.base_url}/health", 
                timeout=10,
                headers={'User-Agent': 'POS-Production-Monitoring/1.0'}
            )
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                self.consecutive_failures = 0
                self.response_times.append(response_time)
                
                # Mantener solo los últimos 1000 response times
                if len(self.response_times) > 1000:
                    self.response_times = self.response_times[-1000:]
                
                return True, "Sistema saludable", response_time
            else:
                self.consecutive_failures += 1
                self.error_count += 1
                return False, f"HTTP {response.status_code}", response_time
                
        except requests.exceptions.Timeout:
            self.consecutive_failures += 1
            self.error_count += 1
            response_time = (time.time() - start_time) * 1000
            return False, "Timeout", response_time
            
        except requests.exceptions.ConnectionError:
            self.consecutive_failures += 1
            self.error_count += 1
            response_time = (time.time() - start_time) * 1000
            return False, "Connection Error", response_time
            
        except Exception as e:
            self.consecutive_failures += 1
            self.error_count += 1
            response_time = (time.time() - start_time) * 1000
            return False, f"Error: {str(e)}", response_time
        finally:
            self.total_checks += 1
    
    def check_system_resources(self) -> Dict[str, float]:
        """
        Verificar recursos del sistema
        
        Returns:
            Dict[str, float]: Métricas de recursos del sistema
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv
            }
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'network_bytes_sent': 0,
                'network_bytes_recv': 0
            }
    
    def check_docker_containers(self) -> Dict[str, str]:
        """
        Verificar estado de contenedores Docker
        
        Returns:
            Dict[str, str]: Estado de cada contenedor
        """
        try:
            result = subprocess.run(
                ['docker', 'ps', '--format', 'table {{.Names}}\t{{.Status}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                containers = {}
                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            containers[parts[0]] = parts[1]
                return containers
            else:
                return {}
        except Exception as e:
            logger.error(f"Error checking Docker containers: {e}")
            return {}
    
    def check_database_health(self) -> Tuple[bool, str]:
        """
        Verificar salud de la base de datos
        
        Returns:
            Tuple[bool, str]: (is_healthy, message)
        """
        try:
            # Intentar hacer una query simple
            response = requests.get(f"{self.base_url}/api/v1/users", timeout=10)
            
            if response.status_code == 200:
                return True, "Database conectada"
            else:
                return False, f"Database error: HTTP {response.status_code}"
                
        except Exception as e:
            return False, f"Database error: {str(e)}"
    
    def check_api_endpoints(self) -> Dict[str, bool]:
        """
        Verificar endpoints específicos de la API
        
        Returns:
            Dict[str, bool]: Estado de cada endpoint
        """
        endpoints = {
            'health': '/health',
            'users': '/api/v1/users',
            'products': '/api/v1/products',
            'sales': '/api/v1/sales'
        }
        
        results = {}
        
        for name, endpoint in endpoints.items():
            try:
                response = requests.get(
                    f"{self.base_url}{endpoint}", 
                    timeout=5
                )
                results[name] = response.status_code in [200, 401, 403]  # 401/403 son OK para endpoints protegidos
            except:
                results[name] = False
        
        return results
    
    def calculate_metrics(self) -> Dict[str, float]:
        """
        Calcular métricas del sistema
        
        Returns:
            Dict[str, float]: Métricas calculadas
        """
        if not self.response_times:
            return {
                'avg_response_time_ms': 0,
                'max_response_time_ms': 0,
                'min_response_time_ms': 0,
                'error_rate_percent': 0
            }
        
        avg_response_time = sum(self.response_times) / len(self.response_times)
        max_response_time = max(self.response_times)
        min_response_time = min(self.response_times)
        error_rate = (self.error_count / self.total_checks) * 100 if self.total_checks > 0 else 0
        
        return {
            'avg_response_time_ms': round(avg_response_time, 2),
            'max_response_time_ms': round(max_response_time, 2),
            'min_response_time_ms': round(min_response_time, 2),
            'error_rate_percent': round(error_rate, 2)
        }
    
    def check_thresholds(self, metrics: Dict[str, float], system_resources: Dict[str, float]) -> List[str]:
        """
        Verificar si se han excedido los umbrales
        
        Args:
            metrics: Métricas de la aplicación
            system_resources: Recursos del sistema
            
        Returns:
            List[str]: Lista de alertas generadas
        """
        alerts = []
        
        # Verificar response time
        if metrics['avg_response_time_ms'] > self.alert_thresholds['response_time_ms']:
            alerts.append(f"Response time alto: {metrics['avg_response_time_ms']}ms")
        
        # Verificar error rate
        if metrics['error_rate_percent'] > self.alert_thresholds['error_rate_percent']:
            alerts.append(f"Error rate alto: {metrics['error_rate_percent']}%")
        
        # Verificar consecutive failures
        if self.consecutive_failures >= self.alert_thresholds['consecutive_failures']:
            alerts.append(f"Fallos consecutivos: {self.consecutive_failures}")
        
        # Verificar recursos del sistema
        if system_resources['cpu_percent'] > self.alert_thresholds['cpu_usage_percent']:
            alerts.append(f"CPU usage alto: {system_resources['cpu_percent']}%")
        
        if system_resources['memory_percent'] > self.alert_thresholds['memory_usage_percent']:
            alerts.append(f"Memory usage alto: {system_resources['memory_percent']}%")
        
        if system_resources['disk_percent'] > self.alert_thresholds['disk_usage_percent']:
            alerts.append(f"Disk usage alto: {system_resources['disk_percent']}%")
        
        return alerts
    
    def send_alert(self, message: str, severity: str = "WARNING"):
        """
        Enviar alerta por email (si está configurado)
        
        Args:
            message: Mensaje de la alerta
            severity: Severidad (INFO, WARNING, CRITICAL)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_message = f"""
ALERTA DEL SISTEMA POS O'DATA - PRODUCCIÓN
==========================================

Timestamp: {timestamp}
Severidad: {severity}
Sistema: {self.base_url}

Mensaje: {message}

Métricas actuales:
{json.dumps(self.calculate_metrics(), indent=2)}

Recursos del sistema:
{json.dumps(self.check_system_resources(), indent=2)}

Por favor, verificar el estado del sistema inmediatamente.
        """
        
        logger.warning(f"ALERTA [{severity}]: {message}")
        
        if self.alert_email:
            try:
                # Aquí se implementaría el envío de email real
                # Por ahora solo logueamos
                logger.info(f"Email de alerta enviado a: {self.alert_email}")
            except Exception as e:
                logger.error(f"Error enviando email: {e}")
    
    def save_metrics(self, metrics: Dict[str, float], system_resources: Dict[str, float]):
        """
        Guardar métricas en historial
        
        Args:
            metrics: Métricas de la aplicación
            system_resources: Recursos del sistema
        """
        timestamp = datetime.now().isoformat()
        
        record = {
            'timestamp': timestamp,
            'metrics': metrics,
            'system_resources': system_resources,
            'consecutive_failures': self.consecutive_failures,
            'total_checks': self.total_checks
        }
        
        self.metrics_history.append(record)
        
        # Mantener solo los últimos registros
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]
        
        # Guardar en archivo cada 10 registros
        if len(self.metrics_history) % 10 == 0:
            self.save_metrics_to_file()
    
    def save_metrics_to_file(self):
        """Guardar métricas a archivo JSON"""
        try:
            with open('logs/metrics_history.json', 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metrics to file: {e}")
    
    def monitor_continuously(self, check_interval: int = 60):
        """
        Monitorear el sistema continuamente
        
        Args:
            check_interval: Intervalo entre checks en segundos
        """
        logger.info(f"Iniciando monitoreo continuo de producción (intervalo: {check_interval}s)")
        
        while self.monitoring_active:
            try:
                # Check básico de salud
                is_healthy, message, response_time = self.check_health()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if is_healthy:
                    logger.info(f"[{timestamp}] [OK] Sistema saludable - {message} ({response_time:.2f}ms)")
                else:
                    logger.warning(f"[{timestamp}] [ERROR] Sistema no saludable - {message} ({response_time:.2f}ms)")
                
                # Check de recursos del sistema
                system_resources = self.check_system_resources()
                
                # Check de contenedores Docker
                containers = self.check_docker_containers()
                if containers:
                    logger.info(f"Contenedores: {json.dumps(containers, indent=2)}")
                
                # Check de base de datos
                db_healthy, db_message = self.check_database_health()
                if not db_healthy:
                    logger.warning(f"Database issue: {db_message}")
                
                # Check de endpoints específicos
                endpoint_status = self.check_api_endpoints()
                failed_endpoints = [name for name, status in endpoint_status.items() if not status]
                if failed_endpoints:
                    logger.warning(f"Endpoints con problemas: {', '.join(failed_endpoints)}")
                
                # Calcular métricas
                metrics = self.calculate_metrics()
                
                # Guardar métricas
                self.save_metrics(metrics, system_resources)
                
                # Verificar umbrales
                alerts = self.check_thresholds(metrics, system_resources)
                for alert in alerts:
                    self.send_alert(alert, "WARNING")
                
                # Alert por fallos consecutivos
                if self.consecutive_failures >= self.max_consecutive_failures:
                    self.send_alert(
                        f"Sistema caído por {self.consecutive_failures} checks consecutivos", 
                        "CRITICAL"
                    )
                
                # Log de métricas cada 10 checks
                if self.total_checks % 10 == 0:
                    logger.info(f"Métricas: {json.dumps(metrics, indent=2)}")
                    logger.info(f"Recursos: {json.dumps(system_resources, indent=2)}")
                
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoreo detenido por el usuario")
                self.monitoring_active = False
                break
            except Exception as e:
                logger.error(f"Error en monitoreo: {e}")
                time.sleep(check_interval)
    
    def run_single_check(self) -> Dict[str, any]:
        """
        Ejecutar un solo check y retornar resultados
        
        Returns:
            Dict: Resultados del check
        """
        is_healthy, message, response_time = self.check_health()
        endpoint_status = self.check_api_endpoints()
        metrics = self.calculate_metrics()
        system_resources = self.check_system_resources()
        containers = self.check_docker_containers()
        db_healthy, db_message = self.check_database_health()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'is_healthy': is_healthy,
            'message': message,
            'response_time_ms': response_time,
            'endpoint_status': endpoint_status,
            'metrics': metrics,
            'system_resources': system_resources,
            'containers': containers,
            'database_healthy': db_healthy,
            'database_message': db_message,
            'consecutive_failures': self.consecutive_failures
        }

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de Monitoring de Producción - POS O\'Data')
    parser.add_argument('--url', default='http://localhost', help='URL base del sistema')
    parser.add_argument('--interval', type=int, default=60, help='Intervalo de checks en segundos')
    parser.add_argument('--email', help='Email para alertas')
    parser.add_argument('--single-check', action='store_true', help='Ejecutar un solo check')
    
    args = parser.parse_args()
    
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Inicializar monitoring
    monitor = ProductionMonitoring(args.url, args.email)
    
    if args.single_check:
        # Ejecutar un solo check
        result = monitor.run_single_check()
        print(json.dumps(result, indent=2))
    else:
        # Monitoreo continuo
        monitor.monitor_continuously(args.interval)

if __name__ == "__main__":
    main()
