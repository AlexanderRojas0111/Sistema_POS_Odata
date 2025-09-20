"""
API de Analytics Avanzado - Sistema POS Sabrositas
Endpoints para dashboard, métricas y análisis con IA
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime, timedelta

from app.services.analytics_service import analytics_service
from app.middleware.rbac_middleware import require_permission
from app.models.user import User

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/v1/analytics')

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_permission('analytics:read')
def get_dashboard_metrics():
    """
    Obtener métricas completas del dashboard
    
    Query Parameters:
    - period_days: Número de días para el análisis (default: 7)
    """
    try:
        # Obtener parámetros
        period_days = request.args.get('period_days', 7, type=int)
        
        # Validar período
        if period_days < 1 or period_days > 365:
            return jsonify({
                'error': 'El período debe estar entre 1 y 365 días'
            }), 400
        
        # Obtener métricas
        metrics = analytics_service.get_dashboard_metrics(period_days)
        
        logger.info(f"Dashboard metrics requested for {period_days} days")
        
        return jsonify({
            'success': True,
            'data': metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Error en get_dashboard_metrics: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': str(e) if logger.level == logging.DEBUG else None
        }), 500

@analytics_bp.route('/sales-timeline', methods=['GET'])
@jwt_required()
@require_permission('analytics:read')
def get_sales_timeline():
    """
    Obtener timeline detallado de ventas
    
    Query Parameters:
    - start_date: Fecha de inicio (YYYY-MM-DD)
    - end_date: Fecha de fin (YYYY-MM-DD)
    - granularity: hour, day, week, month (default: day)
    """
    try:
        # Obtener parámetros
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        granularity = request.args.get('granularity', 'day')
        
        # Fechas por defecto (últimos 30 días)
        if not start_date_str or not end_date_str:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        else:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }), 400
        
        # Validar granularidad
        if granularity not in ['hour', 'day', 'week', 'month']:
            return jsonify({
                'error': 'Granularidad debe ser: hour, day, week, month'
            }), 400
        
        # Obtener timeline
        timeline = analytics_service._get_sales_timeline(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': {
                'timeline': timeline,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'granularity': granularity
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error en get_sales_timeline: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor'
        }), 500

@analytics_bp.route('/top-products', methods=['GET'])
@jwt_required()
@require_permission('analytics:read')
def get_top_products():
    """
    Obtener productos más vendidos
    
    Query Parameters:
    - period_days: Número de días (default: 30)
    - limit: Número de productos (default: 10)
    - category: Filtrar por categoría (opcional)
    """
    try:
        period_days = request.args.get('period_days', 30, type=int)
        limit = request.args.get('limit', 10, type=int)
        category = request.args.get('category')
        
        # Validaciones
        if period_days < 1 or period_days > 365:
            return jsonify({'error': 'Período inválido'}), 400
        
        if limit < 1 or limit > 100:
            return jsonify({'error': 'Límite debe estar entre 1 y 100'}), 400
        
        # Calcular fechas
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Obtener productos
        top_products = analytics_service._get_top_products(start_date, end_date, limit)
        
        # Filtrar por categoría si se especifica
        if category:
            top_products = [p for p in top_products if p['category'] == category]
        
        return jsonify({
            'success': True,
            'data': {
                'products': top_products,
                'period_days': period_days,
                'category_filter': category
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error en get_top_products: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/payment-analysis', methods=['GET'])
@jwt_required()
@require_permission('analytics:read')
def get_payment_analysis():
    """
    Análisis detallado de métodos de pago
    """
    try:
        period_days = request.args.get('period_days', 30, type=int)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        analysis = analytics_service._get_payment_method_analysis(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': {
                'payment_methods': analysis,
                'period_days': period_days,
                'total_methods': len(analysis)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error en get_payment_analysis: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/category-analysis', methods=['GET'])
@jwt_required()
@require_permission('analytics:read')
def get_category_analysis():
    """
    Análisis detallado por categorías
    """
    try:
        period_days = request.args.get('period_days', 30, type=int)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        analysis = analytics_service._get_category_analysis(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': {
                'categories': analysis,
                'period_days': period_days,
                'total_categories': len(analysis)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error en get_category_analysis: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/ai-insights', methods=['GET'])
@jwt_required()
@require_permission('analytics:read')
def get_ai_insights():
    """
    Obtener insights y recomendaciones de IA
    """
    try:
        insights = analytics_service._get_ai_insights()
        
        return jsonify({
            'success': True,
            'data': insights
        }), 200
        
    except Exception as e:
        logger.error(f"Error en get_ai_insights: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/performance-metrics', methods=['GET'])
@jwt_required()
@require_permission('analytics:read')
def get_performance_metrics():
    """
    Métricas de rendimiento del sistema
    """
    try:
        period_days = request.args.get('period_days', 7, type=int)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        metrics = analytics_service._get_performance_metrics(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': metrics
        }), 200
        
    except Exception as e:
        logger.error(f"Error en get_performance_metrics: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@analytics_bp.route('/real-time-stats', methods=['GET'])
@jwt_required()
@require_permission('analytics:read')
def get_real_time_stats():
    """
    Estadísticas en tiempo real (últimas 24 horas)
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(hours=24)
        
        # Métricas básicas de las últimas 24 horas
        basic_metrics = analytics_service._get_basic_metrics(start_date, end_date)
        
        # Timeline por horas
        from sqlalchemy import func, and_
        from app.models.sale import Sale
        from app import db
        
        hourly_stats = db.session.query(
            func.extract('hour', Sale.sale_date).label('hour'),
            func.count(Sale.id).label('sales'),
            func.coalesce(func.sum(Sale.total_amount), 0).label('revenue')
        ).filter(
            and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
        ).group_by(
            func.extract('hour', Sale.sale_date)
        ).order_by(
            func.extract('hour', Sale.sale_date)
        ).all()
        
        hourly_data = []
        for stat in hourly_stats:
            hourly_data.append({
                'hour': int(stat.hour),
                'sales': stat.sales,
                'revenue': float(stat.revenue)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'basic_metrics': basic_metrics,
                'hourly_stats': hourly_data,
                'last_updated': datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error en get_real_time_stats: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# Registrar errores
@analytics_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'error': 'Acceso denegado',
        'message': 'No tienes permisos para acceder a los analytics'
    }), 403

@analytics_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint no encontrado'
    }), 404
