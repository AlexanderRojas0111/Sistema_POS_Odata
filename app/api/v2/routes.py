from flask import Blueprint, jsonify

api_v2 = Blueprint('api_v2', __name__)

@api_v2.route('/')
def api_v2_info():
    """Información sobre la API v2"""
    return jsonify({
        "message": "API v2 de POS Odata - Funcionalidades avanzadas con IA",
        "version": "2.0.0",
        "features": [
            "Búsqueda semántica de productos",
            "Recomendaciones inteligentes",
            "Sugerencias de búsqueda",
            "Análisis de texto con TF-IDF",
            "Embeddings con scikit-learn"
        ],
        "endpoints": {
            "ai_health": "/api/v2/ai/health",
            "semantic_search": "/api/v2/ai/search/semantic",
            "recommendations": "/api/v2/ai/products/{id}/recommendations",
            "suggestions": "/api/v2/ai/search/suggestions",
            "update_embeddings": "/api/v2/ai/embeddings/update",
            "ai_stats": "/api/v2/ai/stats"
        }
    })

# API v2 - Funcionalidades avanzadas con IA
from app.api.v2.endpoints import ai_routes

# Registrar rutas de IA
api_v2.register_blueprint(ai_routes.bp) 