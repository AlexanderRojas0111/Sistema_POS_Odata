#!/usr/bin/env python3
"""
Rutas de Estadísticas - O'Data v2.0.0
=====================================

Endpoints para:
- Estadísticas generales del sistema
- Métricas de rendimiento
- Información del sistema
- Estado de servicios

Autor: Sistema POS Odata
Versión: 2.0.0
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime, timedelta
import logging
import psutil
import os

logger = logging.getLogger(__name__)

bp = Blueprint('stats', __name__, url_prefix='/stats')

@bp.route('/system', methods=['GET'])
def get_system_stats():
    """
    Obtener estadísticas del sistema
    ---
    tags:
      - Estadísticas
    responses:
      200:
        description: Estadísticas del sistema
    """
    try:
        # Estadísticas del sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Estadísticas de la aplicación
        app_stats = {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_available': memory.available // (1024**3),  # GB
            'disk_usage': disk.percent,
            'disk_free': disk.free // (1024**3),  # GB
            'uptime': psutil.boot_time(),
            'python_version': os.sys.version,
            'flask_version': current_app.config.get('FLASK_VERSION', 'Unknown')
        }
        
        return jsonify(app_stats), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del sistema: {e}")
        return jsonify({'error': 'Error obteniendo estadísticas'}), 500

@bp.route('/business', methods=['GET'])
def get_business_stats():
    """
    Obtener estadísticas del negocio
    ---
    tags:
      - Estadísticas
    responses:
      200:
        description: Estadísticas del negocio
    """
    try:
        # Usar la instancia correcta de la base de datos desde la aplicación
        from app import db
        from app.models.product import Product
        from app.models.sale import Sale
        from app.models.user import User
        from app.models.inventory import Inventory
        
        # Contar registros
        total_products = Product.query.count()
        total_sales = Sale.query.count()
        total_users = User.query.count()
        total_inventory = Inventory.query.count()
        
        # Calcular ventas del día
        today = datetime.now().date()
        today_sales = Sale.query.filter(
            db.func.date(Sale.created_at) == today
        ).count()
        
        # Calcular ventas de la semana
        week_ago = today - timedelta(days=7)
        week_sales = Sale.query.filter(
            Sale.created_at >= week_ago
        ).count()
        
        # Calcular ventas del mes
        month_ago = today - timedelta(days=30)
        month_sales = Sale.query.filter(
            Sale.created_at >= month_ago
        ).count()
        
        business_stats = {
            'total_products': total_products,
            'total_sales': total_sales,
            'total_users': total_users,
            'total_inventory': total_inventory,
            'today_sales': today_sales,
            'week_sales': week_sales,
            'month_sales': month_sales,
            'last_updated': datetime.now().isoformat()
        }
        
        return jsonify(business_stats), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del negocio: {e}")
        return jsonify({'error': 'Error obteniendo estadísticas'}), 500

@bp.route('/performance', methods=['GET'])
def get_performance_stats():
    """
    Obtener métricas de rendimiento
    ---
    tags:
      - Estadísticas
    responses:
      200:
        description: Métricas de rendimiento
    """
    try:
        # Métricas básicas de rendimiento
        performance_stats = {
            'database_connections': 0,  # Placeholder para implementación futura
            'active_connections': 0,  # Placeholder para implementación futura
            'cache_hit_rate': 0.0,  # Placeholder para implementación futura
            'response_time_avg': 0.0,  # Placeholder para implementación futura
            'requests_per_minute': 0,  # Placeholder para implementación futura
            'error_rate': 0.0,  # Placeholder para implementación futura
            'last_updated': datetime.now().isoformat()
        }
        
        # Intentar obtener métricas reales de la base de datos
        try:
            # Verificar conexión de base de datos
            from app import db
            db.session.execute('SELECT 1')
            performance_stats['database_status'] = 'connected'
        except Exception as e:
            performance_stats['database_status'] = 'error'
            performance_stats['database_error'] = str(e)
        
        return jsonify(performance_stats), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de rendimiento: {e}")
        return jsonify({'error': 'Error obteniendo métricas'}), 500

@bp.route('/health/detailed', methods=['GET'])
def get_detailed_health():
    """
    Obtener estado detallado de salud del sistema
    ---
    tags:
      - Estadísticas
    responses:
      200:
        description: Estado de salud detallado
    """
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'database': 'healthy',
                'redis': 'unknown',
                'file_system': 'healthy',
                'memory': 'healthy'
            },
            'checks': {
                'database_connection': True,
                'disk_space': True,
                'memory_usage': True
            }
        }
        
        # Verificar base de datos
        try:
            from app import db
            db.session.execute('SELECT 1')
            health_status['checks']['database_connection'] = True
        except Exception:
            health_status['checks']['database_connection'] = False
            health_status['services']['database'] = 'unhealthy'
            health_status['status'] = 'degraded'
        
        # Verificar espacio en disco
        try:
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                health_status['checks']['disk_space'] = False
                health_status['services']['file_system'] = 'warning'
                health_status['status'] = 'degraded'
        except Exception:
            health_status['checks']['disk_space'] = False
            health_status['services']['file_system'] = 'unknown'
        
        # Verificar uso de memoria
        try:
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                health_status['checks']['memory_usage'] = False
                health_status['services']['memory'] = 'warning'
                health_status['status'] = 'degraded'
        except Exception:
            health_status['checks']['memory_usage'] = False
            health_status['services']['memory'] = 'unknown'
        
        # Determinar estado general
        if not all(health_status['checks'].values()):
            health_status['status'] = 'unhealthy'
        
        return jsonify(health_status), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de salud: {e}")
        return jsonify({
            'status': 'error',
            'error': 'Error obteniendo estado de salud',
            'timestamp': datetime.now().isoformat()
        }), 500

@bp.route('/version', methods=['GET'])
def get_version_info():
    """
    Obtener información de versión
    ---
    tags:
      - Estadísticas
    responses:
      200:
        description: Información de versión
    """
    try:
        version_info = {
            'application': 'O\'Data POS System',
            'version': '2.0.0',
            'build_date': '2024-01-01',
            'python_version': os.sys.version,
            'flask_version': current_app.config.get('FLASK_VERSION', 'Unknown'),
            'environment': current_app.config.get('ENV', 'development'),
            'database_url': current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown').split('://')[0] if current_app.config.get('SQLALCHEMY_DATABASE_URI') else 'Unknown'
        }
        
        return jsonify(version_info), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo información de versión: {e}")
        return jsonify({'error': 'Error obteniendo información de versión'}), 500
