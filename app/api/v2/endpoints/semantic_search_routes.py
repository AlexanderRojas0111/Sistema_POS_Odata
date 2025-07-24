from flask import Blueprint, request, jsonify
from app.services.ai.semantic_search import SemanticSearchService
from app.core.database import db_session

bp = Blueprint('semantic_search', __name__, url_prefix='/search')
search_service = SemanticSearchService()

@bp.route('/semantic', methods=['GET'])
def semantic_search():
    """Búsqueda semántica de productos"""
    try:
        query = request.args.get('q')
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        with db_session() as session:
            results = search_service.search_products(
                session=session,
                query=query,
                limit=limit
            )
            
            return jsonify({
                'query': query,
                'results': [product.to_dict() for product in results]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/hybrid', methods=['GET'])
def hybrid_search():
    """Búsqueda híbrida (semántica + tradicional)"""
    try:
        query = request.args.get('q')
        category = request.args.get('category')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        with db_session() as session:
            results = search_service.hybrid_search(
                session=session,
                query=query,
                category=category,
                min_price=min_price,
                max_price=max_price,
                limit=limit
            )
            
            return jsonify({
                'query': query,
                'filters': {
                    'category': category,
                    'price_range': [min_price, max_price] if min_price or max_price else None
                },
                'results': [product.to_dict() for product in results]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/embeddings', methods=['POST'])
def generate_embeddings():
    """Genera embeddings para un texto"""
    try:
        data = request.get_json()
        text = data.get('text')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        embedding = search_service.generate_embedding(text)
        
        return jsonify({
            'text': text,
            'embedding': embedding.tolist()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 