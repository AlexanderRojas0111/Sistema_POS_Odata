"""
API v1 - Sistema POS O'Data
==========================
API REST v1 con endpoints enterprise.
"""

from flask import Blueprint

api_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Importar endpoints
from . import sales, products, users, health, simple_users, simple_products, auth, inventory, electronic_invoice, support_document, digital_certificate

# Registrar blueprints
api_bp.register_blueprint(sales.sales_bp)
api_bp.register_blueprint(products.products_bp)
api_bp.register_blueprint(users.users_bp)
api_bp.register_blueprint(health.health_bp)
api_bp.register_blueprint(auth.auth_bp)
api_bp.register_blueprint(inventory.inventory_bp)
api_bp.register_blueprint(electronic_invoice.electronic_invoice_bp)
api_bp.register_blueprint(support_document.support_document_bp)
api_bp.register_blueprint(digital_certificate.digital_certificate_bp)

# Registrar endpoints simplificados
api_bp.register_blueprint(simple_users.simple_users_bp)
api_bp.register_blueprint(simple_products.simple_products_bp)
