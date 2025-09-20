"""
Quotation API v1 - Sistema POS Sabrositas
=========================================
API endpoints para gestión de cotizaciones y presupuestos.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, Any
import logging
from datetime import datetime, date

from app.services.quotation_service import QuotationService
from app.exceptions import BusinessLogicError, ValidationError

logger = logging.getLogger(__name__)

# Crear blueprint
quotation_bp = Blueprint('quotation', __name__)

# Inicializar servicio
quotation_service = QuotationService()

# ==================== COTIZACIONES ====================

@quotation_bp.route('/quotations', methods=['POST'])
@jwt_required()
def create_quotation():
    """Crear nueva cotización"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        # Agregar user_id del token JWT
        current_user_id = get_jwt_identity()
        data['user_id'] = current_user_id
        
        quotation = quotation_service.create_quotation(data)
        return jsonify({
            'message': 'Cotización creada exitosamente',
            'quotation': quotation.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando cotización: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@quotation_bp.route('/quotations', methods=['GET'])
@jwt_required()
def get_quotations():
    """Obtener lista de cotizaciones"""
    try:
        status = request.args.get('status')
        customer_id = request.args.get('customer_id', type=int)
        user_id = request.args.get('user_id', type=int)
        
        quotations = quotation_service.get_quotations(
            status=status,
            customer_id=customer_id,
            user_id=user_id
        )
        
        return jsonify({
            'quotations': [quotation.to_dict() for quotation in quotations],
            'total': len(quotations)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo cotizaciones: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@quotation_bp.route('/quotations/<int:quotation_id>', methods=['GET'])
@jwt_required()
def get_quotation(quotation_id):
    """Obtener cotización por ID"""
    try:
        quotation = quotation_service.get_quotation(quotation_id)
        if not quotation:
            return jsonify({'error': 'Cotización no encontrada'}), 404
        
        return jsonify({'quotation': quotation.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo cotización: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@quotation_bp.route('/quotations/<int:quotation_id>', methods=['PUT'])
@jwt_required()
def update_quotation(quotation_id):
    """Actualizar cotización"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        quotation = quotation_service.update_quotation(quotation_id, data)
        return jsonify({
            'message': 'Cotización actualizada exitosamente',
            'quotation': quotation.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error actualizando cotización: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@quotation_bp.route('/quotations/<int:quotation_id>', methods=['DELETE'])
@jwt_required()
def delete_quotation(quotation_id):
    """Eliminar cotización"""
    try:
        success = quotation_service.delete_quotation(quotation_id)
        if success:
            return jsonify({'message': 'Cotización eliminada exitosamente'}), 200
        else:
            return jsonify({'error': 'Error eliminando cotización'}), 400
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error eliminando cotización: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@quotation_bp.route('/quotations/customer/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_quotations_by_customer(customer_id):
    """Obtener cotizaciones por cliente"""
    try:
        quotations = quotation_service.get_quotations_by_customer(customer_id)
        
        return jsonify({
            'quotations': [quotation.to_dict() for quotation in quotations],
            'total': len(quotations)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo cotizaciones por cliente: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@quotation_bp.route('/quotations/expired', methods=['GET'])
@jwt_required()
def get_expired_quotations():
    """Obtener cotizaciones vencidas"""
    try:
        quotations = quotation_service.get_expired_quotations()
        
        return jsonify({
            'quotations': [quotation.to_dict() for quotation in quotations],
            'total': len(quotations)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo cotizaciones vencidas: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== APROBACIÓN ====================

@quotation_bp.route('/quotations/<int:quotation_id>/submit', methods=['POST'])
@jwt_required()
def submit_for_approval(quotation_id):
    """Enviar cotización para aprobación"""
    try:
        current_user_id = get_jwt_identity()
        
        quotation = quotation_service.submit_for_approval(quotation_id, current_user_id)
        return jsonify({
            'message': 'Cotización enviada para aprobación',
            'quotation': quotation.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error enviando cotización para aprobación: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@quotation_bp.route('/quotations/<int:quotation_id>/approve', methods=['POST'])
@jwt_required()
def approve_quotation(quotation_id):
    """Aprobar cotización"""
    try:
        data = request.get_json() or {}
        current_user_id = get_jwt_identity()
        comments = data.get('comments')
        
        quotation = quotation_service.approve_quotation(quotation_id, current_user_id, comments)
        return jsonify({
            'message': 'Cotización aprobada exitosamente',
            'quotation': quotation.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error aprobando cotización: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@quotation_bp.route('/quotations/<int:quotation_id>/reject', methods=['POST'])
@jwt_required()
def reject_quotation(quotation_id):
    """Rechazar cotización"""
    try:
        data = request.get_json()
        if not data or not data.get('rejection_reason'):
            return jsonify({'error': 'Razón de rechazo requerida'}), 400
        
        current_user_id = get_jwt_identity()
        rejection_reason = data['rejection_reason']
        
        quotation = quotation_service.reject_quotation(quotation_id, current_user_id, rejection_reason)
        return jsonify({
            'message': 'Cotización rechazada',
            'quotation': quotation.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error rechazando cotización: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== CONVERSIÓN A VENTA ====================

@quotation_bp.route('/quotations/<int:quotation_id>/convert', methods=['POST'])
@jwt_required()
def convert_to_sale(quotation_id):
    """Convertir cotización a venta"""
    try:
        current_user_id = get_jwt_identity()
        
        sale = quotation_service.convert_to_sale(quotation_id, current_user_id)
        return jsonify({
            'message': 'Cotización convertida a venta exitosamente',
            'sale': {
                'id': sale.id,
                'total_amount': float(sale.total_amount),
                'created_at': sale.created_at.isoformat() if sale.created_at else None
            }
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error convirtiendo cotización a venta: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== PLANTILLAS ====================

@quotation_bp.route('/templates', methods=['POST'])
@jwt_required()
def create_template():
    """Crear plantilla de cotización"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Datos requeridos'}), 400
        
        template = quotation_service.create_template(data)
        return jsonify({
            'message': 'Plantilla creada exitosamente',
            'template': template.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessLogicError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creando plantilla: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@quotation_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_templates():
    """Obtener plantillas de cotización"""
    try:
        templates = quotation_service.get_templates()
        
        return jsonify({
            'templates': [template.to_dict() for template in templates],
            'total': len(templates)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo plantillas: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@quotation_bp.route('/templates/<int:template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    """Obtener plantilla por ID"""
    try:
        template = quotation_service.get_template(template_id)
        if not template:
            return jsonify({'error': 'Plantilla no encontrada'}), 404
        
        return jsonify({'template': template.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo plantilla: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@quotation_bp.route('/templates/default', methods=['GET'])
@jwt_required()
def get_default_template():
    """Obtener plantilla por defecto"""
    try:
        template = quotation_service.get_default_template()
        if not template:
            return jsonify({'error': 'No hay plantilla por defecto'}), 404
        
        return jsonify({'template': template.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo plantilla por defecto: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== REPORTES ====================

@quotation_bp.route('/reports/summary', methods=['GET'])
@jwt_required()
def get_quotations_summary():
    """Obtener resumen de cotizaciones"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        summary = quotation_service.get_quotations_summary(start_date, end_date)
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Error generando resumen de cotizaciones: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@quotation_bp.route('/reports/analytics', methods=['GET'])
@jwt_required()
def get_quotation_analytics():
    """Obtener análisis de cotizaciones"""
    try:
        customer_id = request.args.get('customer_id', type=int)
        
        analytics = quotation_service.get_quotation_analytics(customer_id=customer_id)
        
        return jsonify(analytics), 200
        
    except Exception as e:
        logger.error(f"Error generando análisis de cotizaciones: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== DASHBOARD ====================

@quotation_bp.route('/dashboard/summary', methods=['GET'])
@jwt_required()
def get_dashboard_summary():
    """Obtener resumen del dashboard de cotizaciones"""
    try:
        # Resumen general
        general_summary = quotation_service.get_quotations_summary()
        
        # Cotizaciones vencidas
        expired_quotations = quotation_service.get_expired_quotations()
        expired_amount = sum(float(q.total_amount) for q in expired_quotations)
        
        # Análisis
        analytics = quotation_service.get_quotation_analytics()
        
        # Cotizaciones pendientes de aprobación
        pending_quotations = quotation_service.get_quotations(status='pending')
        
        summary = {
            'general': general_summary,
            'expired': {
                'count': len(expired_quotations),
                'amount': expired_amount
            },
            'pending_approval': {
                'count': len(pending_quotations),
                'amount': sum(float(q.total_amount) for q in pending_quotations)
            },
            'analytics': analytics,
            'recent_quotations': [
                {
                    'id': q.id,
                    'quotation_number': q.quotation_number,
                    'title': q.title,
                    'total_amount': float(q.total_amount),
                    'status': q.status,
                    'priority': q.priority,
                    'days_until_expiry': q.days_until_expiry,
                    'created_at': q.created_at.isoformat() if q.created_at else None
                }
                for q in quotation_service.get_quotations()[:10]
            ]
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        logger.error(f"Error generando resumen del dashboard: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
