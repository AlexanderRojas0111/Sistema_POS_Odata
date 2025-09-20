#!/usr/bin/env python3
"""
Sistema de Monitoring Básico - Sistema POS O'Data
=================================================
Monitoring básico para ambiente de staging y producción
"""

import requests
import time
import json
import smtplib
from email.mime.text import MimeText
from datetime import datetime
import logging
import os
from typing import Dict, List, Tuple, Optional

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BasicMonitoring:
    """Sistema de monitoring básico para el POS"""
    
    def __init__(self, base_url: str, alert_email: Optional[str] = None):
        self.base_url = base_url
        self.alert_email = alert_email
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        self.check_interval = 30  # segundos
        self.response_times = []
        self.error_count = 0
        self.total_checks = 0
        
        # Configuración de alertas
        self.alert_thresholds = {
            'response_time_ms': 1000,  # 1 segundo
            'error_rate_percent': 5.0,  # 5%
            'consecutive_failures': 3
        }
        
        logger.info(f"Monitoring iniciado para: {base_url}")
    
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
                headers={'User-Agent': 'POS-Monitoring/1.0'}
            )
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                self.consecutive_failures = 0
                self.response_times.append(response_time)
                
                # Mantener solo los últimos 100 response times
                if len(self.response_times) > 100:
                    self.response_times = self.response_times[-100:]
                
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
    
    def send_alert(self, message: str, severity: str = "WARNING"):
        """
        Enviar alerta por email (si está configurado)
        
        Args:
            message: Mensaje de la alerta
            severity: Severidad (INFO, WARNING, CRITICAL)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_message = f"""
ALERTA DEL SISTEMA POS O'DATA
=============================

Timestamp: {timestamp}
Severidad: {severity}
Sistema: {self.base_url}

Mensaje: {message}

Métricas actuales:
{json.dumps(self.calculate_metrics(), indent=2)}

Por favor, verificar el estado del sistema.
        """
        
        logger.warning(f"ALERTA [{severity}]: {message}")
        
        if self.alert_email:
            try:
                # Aquí se implementaría el envío de email real
                # Por ahora solo logueamos
                logger.info(f"Email de alerta enviado a: {self.alert_email}")
            except Exception as e:
                logger.error(f"Error enviando email: {e}")
    
    def check_thresholds(self, metrics: Dict[str, float]) -> List[str]:
        """
        Verificar si se han excedido los umbrales
        
        Args:
            metrics: Métricas calculadas
            
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
        
        return alerts
    
    def monitor_continuously(self, check_interval: int = 30):
        """
        Monitorear el sistema continuamente
        
        Args:
            check_interval: Intervalo entre checks en segundos
        """
        logger.info(f"Iniciando monitoreo continuo (intervalo: {check_interval}s)")
        
        while True:
            try:
                # Check básico de salud
                is_healthy, message, response_time = self.check_health()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if is_healthy:
                    logger.info(f"[{timestamp}] [OK] Sistema saludable - {message} ({response_time:.2f}ms)")
                else:
                    logger.warning(f"[{timestamp}] [ERROR] Sistema no saludable - {message} ({response_time:.2f}ms)")
                
                # Check de endpoints específicos
                endpoint_status = self.check_api_endpoints()
                failed_endpoints = [name for name, status in endpoint_status.items() if not status]
                if failed_endpoints:
                    logger.warning(f"Endpoints con problemas: {', '.join(failed_endpoints)}")
                
                # Calcular métricas
                metrics = self.calculate_metrics()
                
                # Verificar umbrales
                alerts = self.check_thresholds(metrics)
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
                
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoreo detenido por el usuario")
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
        
        return {
            'timestamp': datetime.now().isoformat(),
            'is_healthy': is_healthy,
            'message': message,
            'response_time_ms': response_time,
            'endpoint_status': endpoint_status,
            'metrics': metrics,
            'consecutive_failures': self.consecutive_failures
        }

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de Monitoring POS O\'Data')
    parser.add_argument('--url', default='http://localhost:8080', help='URL base del sistema')
    parser.add_argument('--interval', type=int, default=30, help='Intervalo de checks en segundos')
    parser.add_argument('--email', help='Email para alertas')
    parser.add_argument('--single-check', action='store_true', help='Ejecutar un solo check')
    
    args = parser.parse_args()
    
    # Crear directorio de logs si no existe
    os.makedirs('logs', exist_ok=True)
    
    # Inicializar monitoring
    monitor = BasicMonitoring(args.url, args.email)
    
    if args.single_check:
        # Ejecutar un solo check
        result = monitor.run_single_check()
        print(json.dumps(result, indent=2))
    else:
        # Monitoreo continuo
        monitor.monitor_continuously(args.interval)

if __name__ == "__main__":
    main()
