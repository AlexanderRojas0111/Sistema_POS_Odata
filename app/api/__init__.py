"""
API Enterprise - Sistema POS O'Data
==================================
API REST con arquitectura enterprise y documentación automática.
"""

from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Importar blueprints específicos
from .v1 import api_bp as v1_bp
