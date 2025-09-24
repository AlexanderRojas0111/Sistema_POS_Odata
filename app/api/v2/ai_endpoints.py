"""
Endpoints de IA - Sistema POS O'Data v2.0
=========================================
Endpoints para funcionalidades de inteligencia artificial con arquitectura enterprise.
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.ai_service import AIService
from app.models.product import Product
from app.models.ai_models import AIModelStatus
from app.utils.response_helpers import success_response, error_response, created_response
from app.middleware.error_handler_enhanced import error_handler, APIError
from app.security.rate_limiter_enhanced import apply_rate_limit
from app.schemas.validation_schemas import AISearchSchema, AIRecommendationSchema
from app import db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Crear blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

# Instancia global del servicio de IA
ai_service = None

def get_ai_service():
    """Obtener instancia del servicio de IA"""
    global ai_service
    if ai_service is None:
        ai_service = AIService()
    return ai_service

@ai_bp.route('/health', methods=['GET'])
@apply_rate_limit('moderate')
@error_handler
def ai_health():
    """Health check del sistema de IA"""
    try:
        ai_service = get_ai_service()
        stats = ai_service.get_ai_stats()
        
        return success_response(
            data={
                'status': 'healthy',
                'version': '2.0.0-ai',
                'stats': stats,
                'timestamp': datetime.utcnow().isoformat()
            },
            message='Sistema de IA funcionando correctamente'
        )
        
    except Exception as e:
        logger.error(f"Error in AI health check: {e}")
        raise APIError("Error en el sistema de IA", 500)

@ai_bp.route('/search/semantic', methods=['POST'])
@apply_rate_limit('moderate')
@error_handler
def semantic_search():
    """Búsqueda semántica de productos"""
    try:
        # Validar datos de entrada
        from app.schemas.validation_schemas import ai_search_schema
        from marshmallow import ValidationError
        data = ai_search_schema.load(request.get_json() or {})
        
        ai_service = get_ai_service()
        results = ai_service.semantic_search(data['query'], data['limit'])
        
        return success_response(
            data={
                'query': data['query'],
                'results': results,
                'total_results': len(results),
                'filters_applied': data.get('filters', {})
            },
            message=f'Búsqueda semántica completada: {len(results)} resultados'
        )
        
    except ValidationError as e:
        logger.warning(f"Validation error in semantic search: {e.messages}")
        return error_response(
            message="Datos de entrada inválidos",
            error_code="VALIDATION_ERROR",
            details=e.messages,
            status_code=400
        )
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        raise APIError("Error en búsqueda semántica", 500)

@ai_bp.route('/products/<int:product_id>/recommendations', methods=['GET'])
@apply_rate_limit('moderate')
@error_handler
def get_product_recommendations(product_id):
    """Obtener recomendaciones para un producto"""
    try:
        # Validar parámetros
        from app.schemas.validation_schemas import ai_recommendation_schema
        data = ai_recommendation_schema.load({
            'product_id': product_id,
            'limit': request.args.get('limit', 5, type=int),
            'algorithm': request.args.get('algorithm', 'collaborative')
        })
        
        ai_service = get_ai_service()
        recommendations = ai_service.get_recommendations(
            data['product_id'], 
            data['limit']
        )
        
        return success_response(
            data={
                'product_id': data['product_id'],
                'recommendations': recommendations,
                'total_recommendations': len(recommendations),
                'algorithm_used': data['algorithm']
            },
            message=f'Recomendaciones generadas: {len(recommendations)} productos'
        )
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise APIError("Error generando recomendaciones", 500)

@ai_bp.route('/search/suggestions', methods=['GET'])
@apply_rate_limit('lenient')
@error_handler
def get_search_suggestions():
    """Obtener sugerencias de búsqueda"""
    try:
        # Validar parámetros
        from app.schemas.validation_schemas import ai_suggestion_schema
        data = ai_suggestion_schema.load({
            'query': request.args.get('q', ''),
            'limit': request.args.get('limit', 10, type=int)
        })
        
        if not data['query'] or len(data['query']) < 2:
            return success_response(
                data={
                    'suggestions': [],
                    'query': data['query']
                },
                message='Query too short for suggestions'
            )
        
        ai_service = get_ai_service()
        suggestions = ai_service.get_search_suggestions(data['query'], data['limit'])
        
        return success_response(
            data={
                'suggestions': suggestions,
                'query': data['query'],
                'total_suggestions': len(suggestions)
            },
            message=f'Sugerencias generadas: {len(suggestions)} resultados'
        )
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        raise APIError("Error obteniendo sugerencias", 500)

@ai_bp.route('/stats', methods=['GET'])
@apply_rate_limit('moderate')
@error_handler
def get_ai_stats():
    """Obtener estadísticas del sistema de IA"""
    try:
        ai_service = get_ai_service()
        stats = ai_service.get_ai_stats()
        
        return success_response(
            data=stats,
            message='Estadísticas del sistema de IA'
        )
        
    except Exception as e:
        logger.error(f"Error getting AI stats: {e}")
        raise APIError("Error obteniendo estadísticas", 500)

@ai_bp.route('/embeddings/update', methods=['POST'])
@apply_rate_limit('strict')
@error_handler
def update_embeddings():
    """Actualizar embeddings del sistema de IA"""
    try:
        ai_service = get_ai_service()
        success = ai_service.initialize_ai_system()
        
        if success:
            return success_response(
                data={
                    'timestamp': datetime.utcnow().isoformat(),
                    'status': 'completed'
                },
                message='Embeddings actualizados correctamente'
            )
        else:
            raise APIError("Error actualizando embeddings", 500)
            
    except Exception as e:
        logger.error(f"Error updating embeddings: {e}")
        raise APIError("Error actualizando embeddings", 500)

@ai_bp.route('/models/status', methods=['GET'])
@apply_rate_limit('moderate')
@error_handler
def get_models_status():
    """Obtener estado de los modelos de IA"""
    try:
        models = AIModelStatus.query.all()
        
        return success_response(
            data={
                'models': [model.to_dict() for model in models],
                'total_models': len(models)
            },
            message='Estado de modelos de IA'
        )
        
    except Exception as e:
        logger.error(f"Error getting models status: {e}")
        raise APIError("Error obteniendo estado de modelos", 500)

@ai_bp.route('/search/history', methods=['GET'])
@apply_rate_limit('moderate')
@error_handler
def get_search_history():
    """Obtener historial de búsquedas"""
    try:
        # Validar parámetros de paginación
        from app.schemas.validation_schemas import pagination_schema
        data = pagination_schema.load({
            'page': request.args.get('page', 1, type=int),
            'per_page': min(request.args.get('per_page', 20, type=int), 100),
            'sort_by': 'created_at',
            'sort_order': 'desc'
        })
        
        search_type = request.args.get('type')
        
        from app.models.ai_models import AISearchLog
        
        query = AISearchLog.query
        
        if search_type:
            query = query.filter(AISearchLog.search_type == search_type)
        
        query = query.order_by(AISearchLog.created_at.desc())
        
        pagination = query.paginate(
            page=data['page'], 
            per_page=data['per_page'], 
            error_out=False
        )
        
        return success_response(
            data={
                'searches': [search.to_dict() for search in pagination.items],
                'pagination': {
                    'page': data['page'],
                    'per_page': data['per_page'],
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                },
                'filters': {
                    'search_type': search_type
                }
            },
            message='Historial de búsquedas'
        )
        
    except Exception as e:
        logger.error(f"Error getting search history: {e}")
        raise APIError("Error obteniendo historial de búsquedas", 500)

@ai_bp.route('/monitoring/health', methods=['GET'])
@apply_rate_limit('lenient')
@error_handler
def ai_monitoring_health():
    """Health check detallado del sistema de IA"""
    try:
        ai_service = get_ai_service()
        stats = ai_service.get_ai_stats()
        
        # Verificar estado de modelos
        models = AIModelStatus.query.all()
        model_status = {
            'total_models': len(models),
            'active_models': len([m for m in models if m.is_trained]),
            'models': [m.to_dict() for m in models]
        }
        
        # Verificar estado general
        overall_status = 'healthy'
        if model_status['active_models'] == 0:
            overall_status = 'warning'
        
        return success_response(
            data={
                'status': overall_status,
                'version': '2.0.0-ai',
                'timestamp': datetime.utcnow().isoformat(),
                'ai_stats': stats,
                'model_status': model_status,
                'checks': {
                    'ai_service': 'healthy',
                    'models': 'healthy' if model_status['active_models'] > 0 else 'warning',
                    'database': 'healthy'
                }
            },
            message='Health check del sistema de IA completado'
        )
        
    except Exception as e:
        logger.error(f"Error in AI monitoring health check: {e}")
        raise APIError("Error en health check del sistema de IA", 500)

@ai_bp.route('/monitoring/metrics', methods=['GET'])
@apply_rate_limit('moderate')
@error_handler
def ai_monitoring_metrics():
    """Métricas detalladas del sistema de IA"""
    try:
        ai_service = get_ai_service()
        stats = ai_service.get_ai_stats()
        
        # Obtener métricas de búsquedas
        from app.models.ai_models import AISearchLog
        from datetime import datetime, timedelta
        
        # Búsquedas en las últimas 24 horas
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_searches = AISearchLog.query.filter(
            AISearchLog.created_at >= yesterday
        ).count()
        
        # Búsquedas por tipo
        search_types = db.session.query(
            AISearchLog.search_type,
            db.func.count(AISearchLog.id)
        ).filter(
            AISearchLog.created_at >= yesterday
        ).group_by(AISearchLog.search_type).all()
        
        return success_response(
            data={
                'timestamp': datetime.utcnow().isoformat(),
                'ai_stats': stats,
                'search_metrics': {
                    'searches_last_24h': recent_searches,
                    'searches_by_type': dict(search_types),
                    'average_response_time': stats.get('avg_response_time', 0)
                },
                'performance': {
                    'uptime': stats.get('uptime', 0),
                    'memory_usage': stats.get('memory_usage', 0),
                    'cpu_usage': stats.get('cpu_usage', 0)
                }
            },
            message='Métricas del sistema de IA'
        )
        
    except Exception as e:
        logger.error(f"Error getting AI monitoring metrics: {e}")
        raise APIError("Error obteniendo métricas del sistema de IA", 500)
