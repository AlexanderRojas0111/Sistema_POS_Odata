#!/usr/bin/env python3
"""
Servicio de Monitoreo Básico - Sistema POS Sabrositas v2.0.0
============================================================
Monitoreo básico de servicios y métricas del sistema
"""

import time
import requests
import logging
import os
import psutil
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BasicMonitoring:
    """Servicio básico de monitoreo"""
    
    def __init__(self):
        self.monitoring_url = os.environ.get('MONITORING_URL', 'http://pos-app-production:8000')
        self.monitoring_interval = int(os.environ.get('MONITORING_INTERVAL', '60'))
        self.alert_email = os.environ.get('ALERT_EMAIL', '')
    
    def check_service_health(self):
        """Verificar salud del servicio principal"""
        try:
            response = requests.get(
                f"{self.monitoring_url}/api/v1/health",
                timeout=10
            )
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"Service health: {health_data.get('status', 'unknown')}")
                return True
            else:
                logger.warning(f"Service health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Service health check error: {e}")
            return False
    
    def check_system_resources(self):
        """Verificar recursos del sistema"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            logger.info(f"System resources - CPU: {cpu_percent}%, Memory: {memory_percent}%, Disk: {disk_percent:.1f}%")
            
            # Alertas básicas
            if cpu_percent > 80:
                logger.warning(f"High CPU usage: {cpu_percent}%")
            
            if memory_percent > 85:
                logger.warning(f"High memory usage: {memory_percent}%")
            
            if disk_percent > 90:
                logger.critical(f"Low disk space: {disk_percent:.1f}%")
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent
            }
            
        except Exception as e:
            logger.error(f"System resource check error: {e}")
            return None
    
    def run_monitoring_loop(self):
        """Ejecutar loop principal de monitoreo"""
        logger.info("Starting basic monitoring service")
        
        while True:
            try:
                logger.info("Running monitoring checks...")
                
                # Verificar salud del servicio
                service_healthy = self.check_service_health()
                
                # Verificar recursos del sistema
                system_resources = self.check_system_resources()
                
                # Log status
                status = "HEALTHY" if service_healthy else "UNHEALTHY"
                logger.info(f"Monitoring cycle complete - Status: {status}")
                
                # Esperar antes del próximo ciclo
                time.sleep(self.monitoring_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring service stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(30)  # Esperar menos tiempo en caso de error

def main():
    """Función principal"""
    monitoring = BasicMonitoring()
    monitoring.run_monitoring_loop()

if __name__ == '__main__':
    main()