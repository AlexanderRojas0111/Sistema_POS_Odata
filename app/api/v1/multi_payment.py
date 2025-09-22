"""
Multi Payment API v1 - Sistema POS O'Data
=========================================
Endpoints para manejar pagos múltiples en ventas.
"""

from flask import Blueprint, request, jsonify
from app.services.multi_payment_service import MultiPaymentService
from app.exceptions import ValidationError, BusinessLogicError
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
multi_payment_bp = Blueprint('multi_payment', __name__)

# Inicializar servicio
multi_payment_service = MultiPaymentService()

@multi_payment_bp.route('/multi-payment/methods', methods=['GET'])
def get_payment_methods():
    """Obtener métodos de pago disponibles"""
    try:
        methods = multi_payment_service.get_available_payment_methods()
        return jsonify({
            'success': True,
            'data': methods
        })
    except Exception as e:
        logger.error(f"Error obteniendo métodos de pago: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@multi_payment_bp.route('/multi-payment/create', methods=['POST'])
def create_multi_payment():
    """Crear un nuevo pago múltiple"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data:
            raise ValidationError("Datos requeridos")
        
        sale_id = data.get('sale_id')
        user_id = data.get('user_id')
        total_amount = data.get('total_amount')
        notes = data.get('notes')
        
        if not sale_id or not user_id or not total_amount:
            raise ValidationError("sale_id, user_id y total_amount son requeridos")
        
        # Crear pago múltiple
        multi_payment = multi_payment_service.create_multi_payment(
            sale_id=sale_id,
            user_id=user_id,
            total_amount=Decimal(str(total_amount)),
            notes=notes
        )
        
        return jsonify({
            'success': True,
            'data': multi_payment.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creando pago múltiple: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@multi_payment_bp.route('/multi-payment/<int:multi_payment_id>/add-payment', methods=['POST'])
def add_payment(multi_payment_id):
    """Agregar un pago al pago múltiple"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("Datos requeridos")
        
        payment_method = data.get('payment_method')
        amount = data.get('amount')
        reference = data.get('reference')
        
        if not payment_method or not amount:
            raise ValidationError("payment_method y amount son requeridos")
        
        # Agregar pago
        payment_detail = multi_payment_service.add_payment(
            multi_payment_id=multi_payment_id,
            payment_method=payment_method,
            amount=Decimal(str(amount)),
            reference=reference,
            bank_name=data.get('bank_name'),
            card_last_four=data.get('card_last_four'),
            phone_number=data.get('phone_number'),
            qr_code=data.get('qr_code'),
            notes=data.get('notes')
        )
        
        return jsonify({
            'success': True,
            'data': payment_detail.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error agregando pago: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@multi_payment_bp.route('/multi-payment/<int:multi_payment_id>/remove-payment/<int:payment_detail_id>', methods=['DELETE'])
def remove_payment(multi_payment_id, payment_detail_id):
    """Remover un pago del pago múltiple"""
    try:
        success = multi_payment_service.remove_payment(multi_payment_id, payment_detail_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Pago removido exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Pago no encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"Error removiendo pago: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@multi_payment_bp.route('/multi-payment/<int:multi_payment_id>/summary', methods=['GET'])
def get_payment_summary(multi_payment_id):
    """Obtener resumen del pago múltiple"""
    try:
        summary = multi_payment_service.get_payment_summary(multi_payment_id)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@multi_payment_bp.route('/multi-payment/validate', methods=['POST'])
def validate_payment_combination():
    """Validar una combinación de pagos"""
    try:
        data = request.get_json()
        
        if not data or 'payments' not in data:
            raise ValidationError("Lista de pagos requerida")
        
        is_valid, message = multi_payment_service.validate_payment_combination(data['payments'])
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'message': message
        })
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error validando pagos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@multi_payment_bp.route('/multi-payment/suggestions', methods=['POST'])
def get_payment_suggestions():
    """Obtener sugerencias de combinaciones de pago"""
    try:
        data = request.get_json()
        
        if not data or 'total_amount' not in data:
            raise ValidationError("total_amount requerido")
        
        total_amount = Decimal(str(data['total_amount']))
        available_cash = Decimal(str(data.get('available_cash', 0)))
        
        suggestions = multi_payment_service.suggest_payment_combinations(
            total_amount=total_amount,
            available_cash=available_cash
        )
        
        return jsonify({
            'success': True,
            'data': suggestions
        })
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error obteniendo sugerencias: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@multi_payment_bp.route('/multi-payment/calculate-change', methods=['POST'])
def calculate_change():
    """Calcular el cambio a entregar"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("Datos requeridos")
        
        total_amount = Decimal(str(data['total_amount']))
        payments = data.get('payments', [])
        
        change = multi_payment_service.calculate_change(total_amount, payments)
        
        return jsonify({
            'success': True,
            'data': {
                'change_amount': float(change),
                'change_formatted': f"${change:,.0f}"
            }
        })
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error calculando cambio: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500

@multi_payment_bp.route('/multi-payment/method-info/<payment_method>', methods=['GET'])
def get_payment_method_info(payment_method):
    """Obtener información detallada de un método de pago"""
    try:
        info = multi_payment_service.get_payment_method_info(payment_method)
        
        return jsonify({
            'success': True,
            'data': info
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo información del método: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor'
        }), 500
