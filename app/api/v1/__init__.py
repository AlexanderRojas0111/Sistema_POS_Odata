"""
API v1 - Sistema POS O'Data
==========================
API REST v1 con endpoints enterprise.
"""

from flask import Blueprint  # type: ignore[reportMissingImports]

api_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Importar endpoints
from . import sales, products, users, health, simple_users, simple_products, auth, inventory, electronic_invoice, support_document, digital_certificate, payroll, accounts_receivable, quotation, dashboard, debug, roles, analytics, simple_reports, reports_final, reports_enhanced, qr_payments, system_stats, multi_payment, monitoring, products_enhanced, users_enhanced

# Registrar blueprints
api_bp.register_blueprint(sales.sales_bp)
api_bp.register_blueprint(products.products_bp)
api_bp.register_blueprint(users.users_bp)
api_bp.register_blueprint(health.health_bp)

# DEBUG: Registro específico de auth blueprint
print(f"DEBUG: Registrando auth blueprint: {auth.auth_bp}")
print(f"DEBUG: Auth blueprint name: {auth.auth_bp.name}")
try:
    api_bp.register_blueprint(auth.auth_bp)
    print("DEBUG: Auth blueprint registrado exitosamente")
except Exception as e:
    print(f"DEBUG ERROR: Error registrando auth blueprint: {e}")

api_bp.register_blueprint(inventory.inventory_bp)
api_bp.register_blueprint(electronic_invoice.electronic_invoice_bp)
api_bp.register_blueprint(support_document.support_document_bp)
api_bp.register_blueprint(digital_certificate.digital_certificate_bp)
api_bp.register_blueprint(payroll.payroll_bp)
api_bp.register_blueprint(accounts_receivable.accounts_receivable_bp)
api_bp.register_blueprint(quotation.quotation_bp)
api_bp.register_blueprint(dashboard.dashboard_bp)

# Registrar endpoints simplificados
api_bp.register_blueprint(simple_users.simple_users_bp)
api_bp.register_blueprint(simple_products.simple_products_bp)

# Registrar debug endpoints
api_bp.register_blueprint(debug.debug_bp)

# Registrar IAM endpoints
api_bp.register_blueprint(roles.roles_bp)

# Registrar Analytics endpoints
api_bp.register_blueprint(analytics.analytics_bp)

# Registrar Simple Reports endpoints
api_bp.register_blueprint(simple_reports.simple_reports_bp)

# Registrar Reports Professional endpoints (SOLUCIÓN FINAL)
# Comentado temporalmente - reports_professional no está implementado
# api_bp.register_blueprint(reports_professional.reports_professional_bp)

# Registrar Reports Final endpoints (SOLUCIÓN DEFINITIVA)
api_bp.register_blueprint(reports_final.reports_final_bp)

# Registrar Reports Enhanced endpoints (MÓDULO MEJORADO CON EXCEL)
api_bp.register_blueprint(reports_enhanced.reports_enhanced_bp)

# Registrar Reports Professional endpoints (MÓDULO PROFESIONAL CON PDF)
# Comentado temporalmente - se implementó en reports_enhanced

# Registrar QR Payments endpoints
api_bp.register_blueprint(qr_payments.qr_payments_bp)
api_bp.register_blueprint(system_stats.system_stats_bp)
api_bp.register_blueprint(multi_payment.multi_payment_bp)

# Registrar Monitoring endpoints
api_bp.register_blueprint(monitoring.monitoring_bp, url_prefix='/monitoring')

# Registrar Enhanced endpoints (con respuestas consistentes)
api_bp.register_blueprint(products_enhanced.products_enhanced_bp, url_prefix='/enhanced')
api_bp.register_blueprint(users_enhanced.users_enhanced_bp, url_prefix='/enhanced')
