from flask import Blueprint

api_v1 = Blueprint('api_v1', __name__)

# Importar rutas específicas
from app.api.v1.endpoints import (
    product_routes,
    inventory_routes,
    sales_routes,  # Usar nueva versión
    user_routes,
    health_routes,
    auth_routes,  # Nuevo blueprint de autenticación
    stats_routes,  # Nuevo blueprint de estadísticas
    search_routes,  # Nuevo blueprint de búsqueda
    reports_routes,  # Nuevo blueprint de reportes
    # customer_routes    # TODO: Implementar
)

# Registrar rutas
api_v1.register_blueprint(product_routes.bp)
api_v1.register_blueprint(inventory_routes.bp)
api_v1.register_blueprint(sales_routes.bp)  # Usar nueva versión
api_v1.register_blueprint(user_routes.bp)
api_v1.register_blueprint(health_routes.bp)
api_v1.register_blueprint(auth_routes.bp)  # Registrar autenticación
api_v1.register_blueprint(stats_routes.bp)  # Registrar estadísticas
api_v1.register_blueprint(search_routes.bp)  # Registrar búsqueda
api_v1.register_blueprint(reports_routes.bp)  # Registrar reportes
# api_v1.register_blueprint(customer_routes.bp)   # TODO: Implementar 