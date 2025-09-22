"""
Dashboard API v1 - Sistema POS Sabrositas
=========================================
Endpoints para dashboard con métricas enterprise
"""

from flask import Blueprint, request, jsonify


from app.container import container
# from app.services.dashboard_service import DashboardService  # Temporalmente comentado
from app.repositories.sale_repository import SaleRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.exceptions import ValidationError, BusinessLogicError
from app.services.auth_service import token_required, get_current_user
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Crear blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Configurar rate limiting


@dashboard_bp.route('/dashboard', methods=['GET'])

def get_dashboard_summary():
    """Obtener resumen del dashboard con métricas principales"""
    try:
        # Obtener parámetros opcionales
        days = request.args.get('days', 30, type=int)
        store_id = request.args.get('store_id', type=int)
        
        # Obtener servicios del container
        sale_repository = container.get(SaleRepository)
        product_repository = container.get(ProductRepository)
        user_repository = container.get(UserRepository)
        
        # Temporalmente usar datos mock mientras se corrige el servicio
        dashboard_data = {
            'sales_today': 0,
            'sales_this_month': 0,
            'total_products': product_repository.count(),
            'total_users': user_repository.count(),
            'low_stock_products': 0,
            'recent_sales': [],
            'top_products': [],
            'sales_trend': []
        }
        
        logger.info(f"Dashboard data retrieved for {days} days", extra={
            'days': days,
            'store_id': store_id,
            'metrics_count': len(dashboard_data)
        })
        
        return jsonify({
            'status': 'success',
            'data': dashboard_data,
            'metadata': {
                'period_days': days,
                'store_id': store_id,
                'generated_at': datetime.now().isoformat()
            }
        })
        
    except ValidationError as e:
        logger.warning(f"Validation error in dashboard: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Error in dashboard: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@dashboard_bp.route('/dashboard/sales-summary', methods=['GET'])

def get_sales_summary():
    """Obtener resumen específico de ventas"""
    try:
        # Obtener servicios
        sale_repository = container.get(SaleRepository)
        product_repository = container.get(ProductRepository)
        user_repository = container.get(UserRepository)
        
        # Temporalmente usar datos mock
        sales_summary = {
            'total_sales': 0,
            'sales_today': 0,
            'average_sale': 0,
            'top_selling_products': []
        }
        
        return jsonify({
            'status': 'success',
            'data': sales_summary
        })
        
    except Exception as e:
        logger.error(f"Error in sales summary: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@dashboard_bp.route('/dashboard/top-products', methods=['GET'])
 
def get_top_products():
    """Obtener productos más vendidos"""
    try:
        limit = request.args.get('limit', 10, type=int)
        days = request.args.get('days', 30, type=int)
        
        # Obtener servicios
        sale_repository = container.get(SaleRepository)
        product_repository = container.get(ProductRepository)
        user_repository = container.get(UserRepository)
        
        # Temporalmente usar datos mock
        top_products = []
        
        return jsonify({
            'status': 'success',
            'data': {
                'top_products': top_products,
                'period_days': days,
                'limit': limit
            }
        })
        
    except Exception as e:
        logger.error(f"Error in top products: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@dashboard_bp.route('/dashboard/real-time', methods=['GET'])

def get_real_time_metrics():
    """Obtener métricas en tiempo real"""
    try:
        # Obtener servicios
        sale_repository = container.get(SaleRepository)
        product_repository = container.get(ProductRepository)
        user_repository = container.get(UserRepository)
        
        # Temporalmente usar datos mock
        real_time_data = {
            'active_users': user_repository.count(),
            'products_count': product_repository.count(),
            'system_status': 'healthy',
            'last_sale': None
        }
        
        return jsonify({
            'status': 'success',
            'data': real_time_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in real-time metrics: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500
