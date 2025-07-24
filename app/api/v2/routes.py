from flask import Blueprint

api_v2 = Blueprint('api_v2', __name__)

# Importar rutas específicas
from app.api.v2.endpoints import (
    semantic_search_routes,
    agent_routes,
    ai_analytics_routes
)

# Registrar rutas
api_v2.register_blueprint(semantic_search_routes.bp)
api_v2.register_blueprint(agent_routes.bp)
api_v2.register_blueprint(ai_analytics_routes.bp) 