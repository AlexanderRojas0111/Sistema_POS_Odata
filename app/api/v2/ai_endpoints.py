"""
Endpoints de IA - Sistema POS O'Data v2.0
=========================================
Endpoints para funcionalidades de inteligencia artificial.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.services.ai_service import AIService
from app.models.product import Product
from app.models.ai_models import AIModelStatus
from app import db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Crear blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/ai')

# Configurar rate limiting
limiter = Limiter(key_func=get_remote_address)

# Instancia global del servicio de IA
ai_service = None

def get_ai_service():
    """Obtener instancia del servicio de IA"""
    global ai_service
    if ai_service is None:
        ai_service = AIService()
    return ai_service

@ai_bp.route('/health', methods=['GET'])
@limiter.limit("100 per minute")
def ai_health():
    """Health check del sistema de IA"""
    try:
        ai_service = get_ai_service()
        stats = ai_service.get_ai_stats()
        
        return jsonify({
            'status': 'healthy',
            'message': 'Sistema de IA funcionando correctamente',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '2.0.0-ai',
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error in AI health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'message': 'Error en el sistema de IA',
            'error': str(e)
        }), 500

@ai_bp.route('/search/semantic', methods=['POST'])
@limiter.limit("50 per minute")
def semantic_search():
    """Búsqueda semántica de productos"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Query is required'
                }
            }), 400
        
        query = data['query']
        limit = data.get('limit', 10)
        
        if not query.strip():
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Query cannot be empty'
                }
            }), 400
        
        ai_service = get_ai_service()
        results = ai_service.semantic_search(query, limit)
        
        return jsonify({
            'status': 'success',
            'data': {
                'query': query,
                'results': results,
                'total_results': len(results)
            },
            'message': f'Búsqueda semántica completada: {len(results)} resultados'
        })
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'Error en búsqueda semántica'
            }
        }), 500

@ai_bp.route('/products/<int:product_id>/recommendations', methods=['GET'])
@limiter.limit("100 per minute")
def get_product_recommendations(product_id):
    """Obtener recomendaciones para un producto"""
    try:
        limit = request.args.get('limit', 5, type=int)
        
        ai_service = get_ai_service()
        recommendations = ai_service.get_recommendations(product_id, limit)
        
        return jsonify({
            'status': 'success',
            'data': {
                'product_id': product_id,
                'recommendations': recommendations,
                'total_recommendations': len(recommendations)
            },
            'message': f'Recomendaciones generadas: {len(recommendations)} productos'
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'Error generando recomendaciones'
            }
        }), 500

@ai_bp.route('/search/suggestions', methods=['GET'])
@limiter.limit("200 per minute")
def get_search_suggestions():
    """Obtener sugerencias de búsqueda"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        
        if not query or len(query) < 2:
            return jsonify({
                'status': 'success',
                'data': {
                    'suggestions': [],
                    'query': query
                }
            })
        
        ai_service = get_ai_service()
        suggestions = ai_service.get_search_suggestions(query, limit)
        
        return jsonify({
            'status': 'success',
            'data': {
                'suggestions': suggestions,
                'query': query,
                'total_suggestions': len(suggestions)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'Error obteniendo sugerencias'
            }
        }), 500

@ai_bp.route('/stats', methods=['GET'])
@limiter.limit("20 per minute")
def get_ai_stats():
    """Obtener estadísticas del sistema de IA"""
    try:
        ai_service = get_ai_service()
        stats = ai_service.get_ai_stats()
        
        return jsonify({
            'status': 'success',
            'data': stats,
            'message': 'Estadísticas del sistema de IA'
        })
        
    except Exception as e:
        logger.error(f"Error getting AI stats: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'Error obteniendo estadísticas'
            }
        }), 500

@ai_bp.route('/embeddings/update', methods=['POST'])
@limiter.limit("5 per minute")
def update_embeddings():
    """Actualizar embeddings del sistema de IA"""
    try:
        ai_service = get_ai_service()
        success = ai_service.initialize_ai_system()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Embeddings actualizados correctamente',
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'error': {
                    'code': 'TRAINING_ERROR',
                    'message': 'Error actualizando embeddings'
                }
            }), 500
            
    except Exception as e:
        logger.error(f"Error updating embeddings: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'Error actualizando embeddings'
            }
        }), 500

@ai_bp.route('/models/status', methods=['GET'])
@limiter.limit("50 per minute")
def get_models_status():
    """Obtener estado de los modelos de IA"""
    try:
        models = AIModelStatus.query.all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'models': [model.to_dict() for model in models]
            },
            'message': 'Estado de modelos de IA'
        })
        
    except Exception as e:
        logger.error(f"Error getting models status: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'Error obteniendo estado de modelos'
            }
        }), 500

@ai_bp.route('/search/history', methods=['GET'])
@limiter.limit("30 per minute")
def get_search_history():
    """Obtener historial de búsquedas"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        search_type = request.args.get('type')
        
        from app.models.ai_models import AISearchLog
        
        query = AISearchLog.query
        
        if search_type:
            query = query.filter(AISearchLog.search_type == search_type)
        
        query = query.order_by(AISearchLog.created_at.desc())
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'searches': [search.to_dict() for search in pagination.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            },
            'message': 'Historial de búsquedas'
        })
        
    except Exception as e:
        logger.error(f"Error getting search history: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'Error obteniendo historial de búsquedas'
            }
        }), 500
