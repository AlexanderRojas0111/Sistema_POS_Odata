from flask import Blueprint, request, jsonify
from app.rag.embeddings import EmbeddingService
from app.vector_store.models import ProductEmbedding
from typing import Dict, Any

semantic_search = Blueprint('semantic_search', __name__)
embedding_service = EmbeddingService()

@semantic_search.route('/api/v2/search/semantic', methods=['POST'])
def semantic_search_products():
    """Endpoint para búsqueda semántica de productos"""
    data = request.get_json()
    query = data.get('query')
    limit = data.get('limit', 5)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
        
    try:
        similar_products = embedding_service.find_similar_products(query, limit)
        return jsonify({
            'query': query,
            'results': similar_products
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@semantic_search.route('/api/v2/search/hybrid', methods=['POST'])
def hybrid_search():
    """Endpoint para búsqueda híbrida (semántica + tradicional)"""
    data = request.get_json()
    query = data.get('query')
    filters = data.get('filters', {})
    limit = data.get('limit', 5)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
        
    try:
        # TODO: Implementar búsqueda híbrida combinando resultados semánticos y filtros tradicionales
        return jsonify({
            'query': query,
            'filters': filters,
            'results': []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@semantic_search.route('/api/v2/embeddings/generate', methods=['POST'])
def generate_embeddings():
    """Endpoint para generar embeddings de productos"""
    try:
        products = Product.query.all()
        product_dicts = [p.to_dict() for p in products]
        embeddings = embedding_service.batch_generate_embeddings(product_dicts)
        
        # TODO: Guardar embeddings en la base de datos
        return jsonify({
            'status': 'success',
            'processed_count': len(embeddings)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 