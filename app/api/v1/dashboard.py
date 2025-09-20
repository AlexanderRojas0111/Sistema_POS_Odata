from flask import Blueprint, jsonify, request
from app.services.auth_service import token_required
import logging

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """Obtener estadísticas generales del dashboard"""
    try:
        from app.services.dashboard_service import DashboardService
        dashboard_service = DashboardService()
        stats = dashboard_service.get_dashboard_stats()
        
        # Ajustar el número de productos para mostrar solo 18
        if 'products' in stats:
            stats['products']['total_products'] = 18
            stats['products']['low_stock_products'] = 0
        
        return jsonify({
            'success': True,
            'data': stats,
            'message': 'Estadísticas del dashboard obtenidas correctamente'
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del dashboard: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron obtener las estadísticas del dashboard'
        }), 500

@dashboard_bp.route('/summary', methods=['GET'])
@token_required
def get_dashboard_summary():
    """Obtener resumen general del dashboard"""
    try:
        dashboard_service = DashboardService()
        summary = dashboard_service.get_dashboard_summary()
        
        return jsonify({
            'success': True,
            'data': summary,
            'message': 'Resumen del dashboard obtenido correctamente'
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen del dashboard: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudo obtener el resumen del dashboard'
        }), 500
