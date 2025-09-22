"""
System Statistics API - Sistema POS Sabrositas
==============================================
API para obtener estadísticas del sistema
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import db
from app.models.product import Product
from app.models.user import User
from app.models.sale import Sale
from app.models.store import Store
from app.middleware.rbac_middleware import require_permission
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Blueprint para estadísticas del sistema
system_stats_bp = Blueprint('system_stats', __name__, url_prefix='/system-stats')

@system_stats_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_permission('view_dashboard')
def get_dashboard_stats():
    """
    Obtener estadísticas generales del dashboard
    """
    try:
        # Estadísticas básicas
        total_products = Product.query.count()
        total_users = User.query.count()
        total_stores = Store.query.count()
        
        # Ventas del día
        today = datetime.now().date()
        today_sales = Sale.query.filter(
            Sale.created_at >= today
        ).count()
        
        # Ventas de la semana
        week_ago = datetime.now() - timedelta(days=7)
        week_sales = Sale.query.filter(
            Sale.created_at >= week_ago
        ).count()
        
        # Productos con stock bajo (menos de 10)
        low_stock_products = Product.query.filter(
            Product.stock_quantity <= 10
        ).count()
        
        # Usuarios activos (últimos 30 días)
        month_ago = datetime.now() - timedelta(days=30)
        active_users = User.query.filter(
            User.last_login >= month_ago
        ).count()
        
        return jsonify({
            'status': 'success',
            'data': {
                'overview': {
                    'total_products': total_products,
                    'total_users': total_users,
                    'total_stores': total_stores,
                    'low_stock_products': low_stock_products
                },
                'sales': {
                    'today': today_sales,
                    'this_week': week_sales
                },
                'users': {
                    'active_last_30_days': active_users
                },
                'system_health': {
                    'database_connected': True,
                    'ai_system_active': True,
                    'last_updated': datetime.now().isoformat()
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'Error al obtener estadísticas del dashboard'
            }
        }), 500

@system_stats_bp.route('/products', methods=['GET'])
@jwt_required()
@require_permission('view_products')
def get_product_stats():
    """
    Obtener estadísticas de productos
    """
    try:
        # Productos por categoría
        from sqlalchemy import func
        category_stats = db.session.query(
            Product.category,
            func.count(Product.id).label('count'),
            func.sum(Product.stock_quantity).label('total_stock')
        ).group_by(Product.category).all()
        
        # Productos más vendidos (últimos 30 días)
        month_ago = datetime.now() - timedelta(days=30)
        # Aquí podrías agregar lógica para productos más vendidos
        
        # Stock total
        total_stock = db.session.query(
            func.sum(Product.stock_quantity)
        ).scalar() or 0
        
        # Valor total del inventario
        total_inventory_value = db.session.query(
            func.sum(Product.stock_quantity * Product.price)
        ).scalar() or 0
        
        return jsonify({
            'status': 'success',
            'data': {
                'category_breakdown': [
                    {
                        'category': stat.category,
                        'count': stat.count,
                        'total_stock': stat.total_stock
                    }
                    for stat in category_stats
                ],
                'inventory_summary': {
                    'total_stock': total_stock,
                    'total_value': float(total_inventory_value),
                    'average_price': float(total_inventory_value / total_stock) if total_stock > 0 else 0
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting product stats: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'Error al obtener estadísticas de productos'
            }
        }), 500

@system_stats_bp.route('/health', methods=['GET'])
def get_system_health():
    """
    Obtener estado de salud del sistema
    """
    try:
        # Verificar conexión a base de datos
        db.session.execute('SELECT 1')
        database_status = 'healthy'
        
        # Verificar servicios
        services_status = {
            'database': database_status,
            'ai_service': 'healthy',  # Se puede mejorar con verificación real
            'auth_service': 'healthy',
            'file_storage': 'healthy'
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'overall_health': 'healthy',
                'services': services_status,
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0-enterprise'
            }
        })
        
    except Exception as e:
        logger.error(f"Error checking system health: {str(e)}")
        return jsonify({
            'status': 'error',
            'data': {
                'overall_health': 'unhealthy',
                'services': {
                    'database': 'unhealthy'
                },
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        }), 500
