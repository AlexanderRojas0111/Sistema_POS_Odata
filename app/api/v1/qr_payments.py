"""
QR Payments API - Sistema POS Sabrositas
========================================
API para manejar pagos con códigos QR
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.sale import Sale
from app.models.user import User
from app import db
from app.middleware.rbac_middleware import require_permission
from app.exceptions import ValidationError, PaymentError
import uuid
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    qrcode = None  # Para evitar errores de referencia
import io
import base64
from datetime import datetime, timedelta
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Blueprint para QR Payments
qr_payments_bp = Blueprint('qr_payments', __name__, url_prefix='/qr-payments')

@qr_payments_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_payment_qr():
    """
    Generar código QR para pago
    """
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['amount', 'payment_method', 'merchant_name']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f"Campo requerido: {field}")
        
        amount = float(data['amount'])
        payment_method = data['payment_method']
        merchant_name = data.get('merchant_name', 'Sistema POS Sabrositas')
        
        # Validar método de pago QR
        valid_qr_methods = ['nequi_qr', 'daviplata_qr', 'qr_generic']
        if payment_method not in valid_qr_methods:
            raise ValidationError(f"Método de pago QR no válido: {payment_method}")
        
        # Generar ID de transacción único
        transaction_id = f"QR_{uuid.uuid4().hex[:8].upper()}_{int(datetime.now().timestamp())}"
        
        # Crear datos del QR según el método de pago
        qr_data = create_qr_data(amount, payment_method, merchant_name, transaction_id)
        
        # Generar código QR
        qr_code = generate_qr_code(qr_data)
        
        # Obtener información del usuario actual
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Crear registro de transacción QR (sin completar aún)
        qr_transaction = {
            'transaction_id': transaction_id,
            'amount': amount,
            'payment_method': payment_method,
            'merchant_name': merchant_name,
            'qr_data': qr_data,
            'qr_code': qr_code,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            'created_by': user.username if user else 'system'
        }
        
        logger.info(f"QR generado para transacción {transaction_id}, monto: ${amount}")
        
        return jsonify({
            'success': True,
            'data': qr_transaction,
            'message': 'Código QR generado exitosamente'
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Error de validación en generate_payment_qr: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
        
    except Exception as e:
        logger.error(f"Error generando QR: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Error interno del servidor'
            }
        }), 500

@qr_payments_bp.route('/verify/<transaction_id>', methods=['GET'])
@jwt_required()
def verify_payment_status(transaction_id):
    """
    Verificar estado de pago QR
    """
    try:
        # En un sistema real, esto consultaría con el proveedor de pagos
        # Por ahora, simulamos la verificación
        
        # Simular diferentes estados
        import random
        statuses = ['pending', 'completed', 'failed', 'expired']
        weights = [0.4, 0.4, 0.1, 0.1]  # 40% pending, 40% completed, etc.
        
        status = random.choices(statuses, weights=weights)[0]
        
        payment_info = {
            'transaction_id': transaction_id,
            'status': status,
            'verified_at': datetime.utcnow().isoformat(),
            'payment_confirmed': status == 'completed'
        }
        
        if status == 'completed':
            payment_info.update({
                'payment_method': 'qr_payment',
                'payment_reference': f"QR_REF_{transaction_id}",
                'confirmed_amount': None  # Se obtendría del proveedor
            })
        
        return jsonify({
            'success': True,
            'data': payment_info,
            'message': f'Estado de pago verificado: {status}'
        })
        
    except Exception as e:
        logger.error(f"Error verificando pago QR {transaction_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VERIFICATION_ERROR',
                'message': 'Error verificando estado del pago'
            }
        }), 500

@qr_payments_bp.route('/complete/<transaction_id>', methods=['POST'])
@jwt_required()
def complete_qr_payment(transaction_id):
    """
    Completar pago QR y crear venta
    """
    try:
        data = request.get_json()
        
        # Validar datos de la venta
        required_fields = ['items', 'customer_name']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f"Campo requerido para completar venta: {field}")
        
        # Obtener usuario actual
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            raise ValidationError("Usuario no encontrado")
        
        # Crear la venta
        sale_data = {
            'customer_name': data['customer_name'],
            'customer_phone': data.get('customer_phone', ''),
            'customer_email': data.get('customer_email', ''),
            'customer_address': data.get('customer_address', ''),
            'payment_method': 'qr_payment',  # Método genérico para QR
            'payment_reference': transaction_id,
            'notes': f"Pago QR completado - Transacción: {transaction_id}",
            'items': data['items'],
            'user_id': user.id
        }
        
        # Aquí se integraría con el servicio de ventas existente
        # Por ahora, crear una venta básica
        
        total_amount = sum(item['quantity'] * item['unit_price'] for item in data['items'])
        tax_amount = total_amount * 0.19  # IVA 19%
        final_total = total_amount + tax_amount
        
        sale = Sale(
            customer_name=data['customer_name'],
            customer_phone=data.get('customer_phone', ''),
            customer_email=data.get('customer_email', ''),
            customer_address=data.get('customer_address', ''),
            subtotal=total_amount,
            tax_amount=tax_amount,
            total_amount=final_total,
            payment_method='qr_payment',
            payment_reference=transaction_id,
            notes=f"Pago QR completado - Transacción: {transaction_id}",
            user_id=user.id
        )
        
        db.session.add(sale)
        db.session.commit()
        
        logger.info(f"Venta QR completada: {sale.id}, transacción: {transaction_id}")
        
        return jsonify({
            'success': True,
            'data': {
                'sale_id': sale.id,
                'transaction_id': transaction_id,
                'total_amount': float(final_total),
                'payment_method': 'qr_payment',
                'status': 'completed'
            },
            'message': 'Pago QR completado exitosamente'
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Error de validación en complete_qr_payment: {str(e)}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
        
    except Exception as e:
        logger.error(f"Error completando pago QR {transaction_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'COMPLETION_ERROR',
                'message': 'Error completando el pago QR'
            }
        }), 500

def create_qr_data(amount: float, payment_method: str, merchant_name: str, transaction_id: str) -> str:
    """
    Crear datos específicos del QR según el método de pago
    """
    if payment_method == 'nequi_qr':
        return f"nequi://payment?amount={amount}&merchant={merchant_name.replace(' ', '%20')}&reference={transaction_id}"
    
    elif payment_method == 'daviplata_qr':
        return f"daviplata://payment?amount={amount}&merchant={merchant_name.replace(' ', '%20')}&reference={transaction_id}"
    
    elif payment_method == 'qr_generic':
        qr_payload = {
            'amount': amount,
            'currency': 'COP',
            'merchant': merchant_name,
            'transaction_id': transaction_id,
            'timestamp': datetime.utcnow().isoformat(),
            'payment_method': 'qr_generic'
        }
        import json
        return json.dumps(qr_payload)
    
    else:
        raise ValidationError(f"Método de pago QR no soportado: {payment_method}")

def generate_qr_code(data: str) -> str:
    """
    Generar código QR como string base64
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Crear imagen QR
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        logger.error(f"Error generando código QR: {str(e)}")
        raise PaymentError("Error generando código QR")

# Manejo de errores
@qr_payments_bp.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({
        'success': False,
        'error': {
            'code': 'VALIDATION_ERROR',
            'message': str(e)
        }
    }), 400

@qr_payments_bp.errorhandler(PaymentError)
def handle_payment_error(e):
    return jsonify({
        'success': False,
        'error': {
            'code': 'PAYMENT_ERROR',
            'message': str(e)
        }
    }), 400
