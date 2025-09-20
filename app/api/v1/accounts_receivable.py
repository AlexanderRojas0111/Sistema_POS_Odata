"""
Accounts Receivable API v1 - Sistema POS Sabrositas
==================================================
API endpoints para gestión de cartera y cuentas por cobrar.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, Any
import logging
from datetime import datetime, date

from app.services.accounts_receivable_service import AccountsReceivableService
from app.exceptions import BusinessLogicError, ValidationError

logger = logging.getLogger(__name__)

# Crear blueprint
accounts_receivable_bp = Blueprint('accounts_receivable', __name__)

# Inicializar servicio
ar_service = AccountsReceivableService()

# ==================== CLIENTES ====================

@accounts_receivable_bp.route('/customers', methods=['POST'])
@jwt_required()
def create_customer():
    """Crear nuevo cliente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        customer = ar_service.create_customer(data)
        return jsonify({
            'message': 'Cliente creado exitosamente',
            'customer': customer.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando cliente: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/customers', methods=['GET'])
@jwt_required()
def get_customers():
    """Obtener lista de clientes"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        customer_type = request.args.get('customer_type')
        
        customers = ar_service.get_customers(active_only=active_only, customer_type=customer_type)
        
        return jsonify({
            'customers': [customer.to_dict() for customer in customers],
            'total': len(customers)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo clientes: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/customers/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """Obtener cliente por ID"""
    try:
        customer = ar_service.get_customer(customer_id)
        if not customer:
            return jsonify({'error': 'Cliente no encontrado'}), 404
        
        return jsonify({'customer': customer.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo cliente: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/customers/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """Actualizar cliente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        customer = ar_service.update_customer(customer_id, data)
        return jsonify({
            'message': 'Cliente actualizado exitosamente',
            'customer': customer.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error actualizando cliente: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/customers/<int:customer_id>/deactivate', methods=['POST'])
@jwt_required()
def deactivate_customer(customer_id):
    """Desactivar cliente"""
    try:
        customer = ar_service.deactivate_customer(customer_id)
        return jsonify({
            'message': 'Cliente desactivado exitosamente',
            'customer': customer.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error desactivando cliente: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/customers/search', methods=['GET'])
@jwt_required()
def search_customers():
    """Buscar clientes por documento o nombre"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Parámetro de búsqueda requerido'}), 400
        
        # Buscar por documento
        customer_by_doc = ar_service.get_customer_by_document(query)
        if customer_by_doc:
            return jsonify({
                'customers': [customer_by_doc.to_dict()],
                'total': 1
            }), 200
        
        # Buscar por nombre (simplificado)
        customers = ar_service.get_customers(active_only=True)
        matching_customers = [
            c for c in customers 
            if query.lower() in c.name.lower()
        ]
        
        return jsonify({
            'customers': [c.to_dict() for c in matching_customers],
            'total': len(matching_customers)
        }), 200
        
    except Exception as e:
        logger.error(f"Error buscando clientes: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== FACTURAS ====================

@accounts_receivable_bp.route('/invoices', methods=['POST'])
@jwt_required()
def create_invoice():
    """Crear nueva factura"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Agregar user_id del token JWT
        current_user_id = get_jwt_identity()
        data['user_id'] = current_user_id
        
        invoice = ar_service.create_invoice(data)
        return jsonify({
            'message': 'Factura creada exitosamente',
            'invoice': invoice.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando factura: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Obtener factura por ID"""
    try:
        invoice = ar_service.get_invoice(invoice_id)
        if not invoice:
            return jsonify({'error': 'Factura no encontrada'}), 404
        
        return jsonify({'invoice': invoice.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo factura: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/invoices/customer/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_invoices_by_customer(customer_id):
    """Obtener facturas por cliente"""
    try:
        status = request.args.get('status')
        
        invoices = ar_service.get_invoices_by_customer(customer_id, status=status)
        
        return jsonify({
            'invoices': [invoice.to_dict() for invoice in invoices],
            'total': len(invoices)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo facturas por cliente: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/invoices/overdue', methods=['GET'])
@jwt_required()
def get_overdue_invoices():
    """Obtener facturas vencidas"""
    try:
        invoices = ar_service.get_overdue_invoices()
        
        return jsonify({
            'invoices': [invoice.to_dict() for invoice in invoices],
            'total': len(invoices)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo facturas vencidas: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/invoices/summary', methods=['GET'])
@jwt_required()
def get_invoices_summary():
    """Obtener resumen de facturas"""
    try:
        customer_id = request.args.get('customer_id', type=int)
        
        summary = ar_service.get_invoices_summary(customer_id=customer_id)
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen de facturas: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== PAGOS ====================

@accounts_receivable_bp.route('/payments', methods=['POST'])
@jwt_required()
def create_payment():
    """Crear nuevo pago"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Agregar user_id del token JWT
        current_user_id = get_jwt_identity()
        data['user_id'] = current_user_id
        
        payment = ar_service.create_payment(data)
        return jsonify({
            'message': 'Pago registrado exitosamente',
            'payment': payment.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando pago: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/payments/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Obtener pago por ID"""
    try:
        payment = ar_service.get_payment(payment_id)
        if not payment:
            return jsonify({'error': 'Pago no encontrado'}), 404
        
        return jsonify({'payment': payment.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo pago: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/payments/customer/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_payments_by_customer(customer_id):
    """Obtener pagos por cliente"""
    try:
        payments = ar_service.get_payments_by_customer(customer_id)
        
        return jsonify({
            'payments': [payment.to_dict() for payment in payments],
            'total': len(payments)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo pagos por cliente: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/payments/invoice/<int:invoice_id>', methods=['GET'])
@jwt_required()
def get_payments_by_invoice(invoice_id):
    """Obtener pagos por factura"""
    try:
        payments = ar_service.get_payments_by_invoice(invoice_id)
        
        return jsonify({
            'payments': [payment.to_dict() for payment in payments],
            'total': len(payments)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo pagos por factura: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== REPORTES ====================

@accounts_receivable_bp.route('/reports/aging', methods=['GET'])
@jwt_required()
def get_aging_report():
    """Obtener reporte de antigüedad de cartera"""
    try:
        customer_id = request.args.get('customer_id', type=int)
        
        report = ar_service.get_aging_report(customer_id=customer_id)
        
        return jsonify(report), 200
        
    except Exception as e:
        logger.error(f"Error generando reporte de antigüedad: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/reports/customer-statement/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer_statement(customer_id):
    """Obtener estado de cuenta del cliente"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        statement = ar_service.get_customer_statement(customer_id, start_date, end_date)
        
        return jsonify(statement), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error generando estado de cuenta: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@accounts_receivable_bp.route('/reports/collection-efficiency', methods=['GET'])
@jwt_required()
def get_collection_efficiency():
    """Obtener eficiencia de cobranza"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({'error': 'Fechas de inicio y fin son requeridas'}), 400
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        efficiency = ar_service.get_collection_efficiency(start_date, end_date)
        
        return jsonify(efficiency), 200
        
    except Exception as e:
        logger.error(f"Error generando eficiencia de cobranza: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== DASHBOARD ====================

@accounts_receivable_bp.route('/dashboard/summary', methods=['GET'])
@jwt_required()
def get_dashboard_summary():
    """Obtener resumen del dashboard de cartera"""
    try:
        # Resumen general
        general_summary = ar_service.get_invoices_summary()
        
        # Facturas vencidas
        overdue_invoices = ar_service.get_overdue_invoices()
        overdue_amount = sum(float(inv.balance_amount) for inv in overdue_invoices)
        
        # Reporte de antigüedad
        aging_report = ar_service.get_aging_report()
        
        # Clientes con saldo pendiente
        customers_with_balance = ar_service.get_customers(active_only=True)
        customers_with_balance = [c for c in customers_with_balance if c.current_balance > 0]
        
        summary = {
            'general': general_summary,
            'overdue': {
                'count': len(overdue_invoices),
                'amount': overdue_amount
            },
            'aging': aging_report,
            'customers_with_balance': len(customers_with_balance),
            'top_customers': [
                {
                    'id': c.id,
                    'name': c.name,
                    'customer_code': c.customer_code,
                    'balance': float(c.current_balance),
                    'is_overdue': c.is_overdue
                }
                for c in sorted(customers_with_balance, key=lambda x: x.current_balance, reverse=True)[:10]
            ]
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Error generando resumen del dashboard: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
