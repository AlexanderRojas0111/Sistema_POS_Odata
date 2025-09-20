"""
API v2 - Sistema POS O'Data con IA
==================================
API REST v2 con funcionalidades de inteligencia artificial.
"""

from flask import Blueprint

api_v2_bp = Blueprint('api_v2', __name__, url_prefix='/api/v2')

# Importar endpoints de IA
from . import ai_endpoints

# Registrar blueprints
api_v2_bp.register_blueprint(ai_endpoints.ai_bp)
