from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__)

# Importar rutas específicas
from app.api.v1.endpoints import (
    product_routes,
    inventory_routes,
    sales_routes_refactored,  # Usar versión refactorizada
    user_routes,
    health_routes,
    # customer_routes    # TODO: Implementar
)

# Registrar rutas
api_v1.register_blueprint(product_routes.bp)
api_v1.register_blueprint(inventory_routes.bp)
api_v1.register_blueprint(sales_routes_refactored.bp)  # Usar versión refactorizada
api_v1.register_blueprint(user_routes.bp)
api_v1.register_blueprint(health_routes.bp)
# api_v1.register_blueprint(customer_routes.bp)   # TODO: Implementar 