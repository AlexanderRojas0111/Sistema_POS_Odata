#!/usr/bin/env python3
"""
Dashboard de Monitoreo en Tiempo Real
Sistema POS O'Data v2.0.2-enterprise
====================================
Muestra métricas en tiempo real del sistema.
"""

import sys
import time
import requests
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000"

def get_health():
    """Obtener estado de salud del sistema"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_detailed_health():
    """Obtener estado de salud detallado"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health/detailed", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def get_metrics():
    """Obtener métricas del sistema"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health/metrics", timeout=5)
        return response.json() if response.status_code == 200 else None
    except:
        return None

def display_dashboard():
    """Mostrar dashboard de monitoreo"""
    print("\033[2J\033[H")  # Limpiar pantalla
    print("=" * 70)
    print("DASHBOARD DE MONITOREO - Sistema POS O'Data v2.0.2-enterprise")
    print(f"Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # Health básico
    health = get_health()
    if health:
        status_icon = "✅" if health.get('status') == 'healthy' else "❌"
        print(f"Estado General: {status_icon} {health.get('status', 'unknown').upper()}")
        print(f"Versión: {health.get('version', 'N/A')}")
        print(f"Base de Datos: {health.get('database', 'unknown')}")
    else:
        print("Estado General: ❌ No disponible")
    
    print()
    
    # Health detallado
    detailed = get_detailed_health()
    if detailed:
        print("Componentes:")
        print("-" * 70)
        components = detailed.get('components', {})
        for component, data in components.items():
            status = data.get('status', 'unknown')
            icon = "✅" if status == 'healthy' else "❌"
            message = data.get('message', 'N/A')
            print(f"  {icon} {component.upper()}: {message}")
    
    print()
    
    # Métricas
    metrics = get_metrics()
    if metrics:
        print("Métricas del Sistema:")
        print("-" * 70)
        uptime = metrics.get('uptime', {})
        if uptime:
            print(f"  Tiempo activo: {uptime.get('days', 0)} días, {uptime.get('hours', 0)} horas")
        
        requests = metrics.get('requests', {})
        if requests:
            print(f"  Requests totales: {requests.get('total', 0)}")
            print(f"  Requests exitosos: {requests.get('successful', 0)}")
            print(f"  Requests fallidos: {requests.get('failed', 0)}")
        
        response_time = metrics.get('response_time', {})
        if response_time:
            avg = response_time.get('average', 0)
            print(f"  Tiempo de respuesta promedio: {avg:.3f}s")
    
    print()
    print("=" * 70)
    print("Presiona Ctrl+C para salir")

def run_monitoring_dashboard(interval=5):
    """Ejecutar dashboard de monitoreo en tiempo real"""
    try:
        while True:
            display_dashboard()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\nDashboard cerrado.")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Dashboard de monitoreo')
    parser.add_argument('--interval', type=int, default=5, help='Intervalo de actualización en segundos')
    args = parser.parse_args()
    
    run_monitoring_dashboard(args.interval)

