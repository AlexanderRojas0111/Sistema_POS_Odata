"""
Rutas de API v2 - Funcionalidades de IA y búsqueda semántica
"""

from flask import Blueprint, request, jsonify
from app.rag.embeddings import EmbeddingService
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
bp = Blueprint('ai', __name__, url_prefix='/ai')

# Inicialización perezosa del servicio de embeddings
_embedding_service = None

def get_embedding_service():
    """Obtiene el servicio de embeddings con inicialización perezosa"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

@bp.route('/health', methods=['GET'])
def ai_health():
    """Health check para la API de IA"""
    try:
        service = get_embedding_service()
        return jsonify({
            'status': 'healthy',
            'service': 'AI API v2',
            'vocabulary_size': len(service.vectorizer.vocabulary_) if hasattr(service.vectorizer, 'vocabulary_') else 0,
            'total_documents': service.total_documents if hasattr(service, 'total_documents') else 0,
            'is_fitted': service.is_fitted
        })
    except Exception as e:
        logger.error(f"Error en health check de IA: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@bp.route('/search/semantic', methods=['POST'])
def semantic_search():
    """
    Búsqueda semántica de productos
    
    Body:
    {
        "query": "arepa con carne y queso",
        "limit": 5
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Se requiere el campo "query"'
            }), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({
                'error': 'La consulta no puede estar vacía'
            }), 400
        
        limit = min(data.get('limit', 5), 20)  # Máximo 20 resultados
        
        # Realizar búsqueda semántica
        service = get_embedding_service()
        results = service.find_similar_products(query, limit)
        
        return jsonify({
            'query': query,
            'results': results,
            'total_found': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error en búsqueda semántica: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': 'Por favor contacte al administrador'
        }), 500

@bp.route('/products/<int:product_id>/recommendations', methods=['GET'])
def get_product_recommendations(product_id):
    """
    Obtiene recomendaciones basadas en un producto específico
    
    Query params:
    - limit: número máximo de recomendaciones (default: 3, max: 10)
    """
    try:
        limit = min(int(request.args.get('limit', 3)), 10)
        
        service = get_embedding_service()
        recommendations = service.generate_recommendations(product_id, limit)
        
        if not recommendations:
            return jsonify({
                'product_id': product_id,
                'recommendations': [],
                'message': 'No se encontraron recomendaciones para este producto'
            })
        
        return jsonify({
            'product_id': product_id,
            'recommendations': recommendations,
            'total_recommendations': len(recommendations)
        })
        
    except ValueError:
        return jsonify({
            'error': 'El parámetro "limit" debe ser un número válido'
        }), 400
    except Exception as e:
        logger.error(f"Error obteniendo recomendaciones para producto {product_id}: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': 'Por favor contacte al administrador'
        }), 500

@bp.route('/search/suggestions', methods=['GET'])
def get_search_suggestions():
    """
    Obtiene sugerencias de búsqueda basadas en una consulta parcial
    
    Query params:
    - q: consulta parcial
    - limit: número máximo de sugerencias (default: 5, max: 10)
    """
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                'error': 'Se requiere el parámetro "q" con la consulta parcial'
            }), 400
        
        if len(query) < 2:
            return jsonify({
                'query': query,
                'suggestions': [],
                'message': 'La consulta debe tener al menos 2 caracteres'
            })
        
        limit = min(int(request.args.get('limit', 5)), 10)
        
        service = get_embedding_service()
        suggestions = service.get_search_suggestions(query, limit)
        
        return jsonify({
            'query': query,
            'suggestions': suggestions,
            'total_suggestions': len(suggestions)
        })
        
    except ValueError:
        return jsonify({
            'error': 'El parámetro "limit" debe ser un número válido'
        }), 400
    except Exception as e:
        logger.error(f"Error obteniendo sugerencias para '{request.args.get('q', '')}': {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': 'Por favor contacte al administrador'
        }), 500

@bp.route('/embeddings/update', methods=['POST'])
def update_embeddings():
    """
    Actualiza los embeddings para todos los productos
    (Útil después de agregar nuevos productos)
    """
    try:
        service = get_embedding_service()
        result = service.update_embeddings_for_all_products()
        
        if result.get('success'):
            return jsonify({
                'message': 'Embeddings actualizados exitosamente',
                'details': result
            })
        else:
            return jsonify({
                'error': 'Error actualizando embeddings',
                'details': result.get('error')
            }), 500
            
    except Exception as e:
        logger.error(f"Error actualizando embeddings: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': 'Por favor contacte al administrador'
        }), 500

@bp.route('/products/<int:product_id>/embedding', methods=['GET'])
def get_product_embedding(product_id):
    """
    Obtiene el embedding de un producto específico (para debugging)
    """
    try:
        from app.models.product import Product
        
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'error': 'Producto no encontrado'
            }), 404
        
        service = get_embedding_service()
        embedding = service.generate_product_embedding(product)
        
        return jsonify({
            'product_id': product_id,
            'product_name': product.name,
            'embedding': embedding
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo embedding para producto {product_id}: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': 'Por favor contacte al administrador'
        }), 500

@bp.route('/stats', methods=['GET'])
def get_ai_stats():
    """
    Obtiene estadísticas del sistema de IA
    """
    try:
        from app.models.product import Product
        
        total_products = Product.query.count()
        service = get_embedding_service()
        stats = service.get_embedding_stats()
        
        return jsonify({
            'total_products_in_db': total_products,
            'service_status': 'active',
            **stats
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de IA: {e}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': 'Por favor contacte al administrador'
        }), 500