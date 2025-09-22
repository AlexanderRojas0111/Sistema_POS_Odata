"""
Sales API v1 - Sistema POS O'Data
================================
Endpoints de ventas con validaciones enterprise.
"""

from flask import Blueprint, request, jsonify, current_app
from app.container import container
from app.services.sale_service import SaleService
from app.repositories.sale_repository import SaleRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.exceptions import ValidationError, BusinessLogicError
from app.security.jwt_utils import decode_token
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/sales', methods=['POST'])
def create_sale():
    """Crear nueva venta"""
    try:
        # Basic validation
        data = request.get_json()
        
        if not data:
            raise ValidationError("Request body is required")
        
        # Obtener servicios del container
        sale_repository = container.get(SaleRepository)
        product_repository = container.get(ProductRepository)
        user_repository = container.get(UserRepository)
        
        sale_service = SaleService(sale_repository, product_repository, user_repository)
        
        # Solución Senior: Extraer user_id del token JWT si no se proporciona
        user_id = data.get('user_id')
        
        # Si no hay user_id, extraerlo del token JWT
        if not user_id:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                try:
                    # Decodificar token para obtener username
                    payload = decode_token(token)
                    username = payload.get('sub')  # 'sub' contiene el username
                    
                    if username:
                        # Buscar usuario por username para obtener ID
                        user = user_repository.get_by_username(username)
                        if user:
                            user_id = user.id
                            logger.info(f"User ID extraído del token: {user_id} para username: {username}")
                        else:
                            raise ValidationError(f"User not found: {username}", field="user_id")
                    else:
                        raise ValidationError("Invalid token: no username found", field="user_id")
                except Exception as e:
                    logger.error(f"Error decoding JWT token: {e}")
                    raise ValidationError("Invalid or expired token", field="authorization")
            else:
                raise ValidationError("user_id is required or valid Authorization header must be provided", field="user_id")
        
        # Verificar si es un pago múltiple
        multi_payments = data.get('multi_payments')
        is_multi_payment = data.get('payment_method') == 'multi_payment'
        
        # Crear venta
        sale = sale_service.create_sale(user_id, data)
        
        # Si es pago múltiple, crear los detalles de pago
        if is_multi_payment and multi_payments:
            from app.services.multi_payment_service import MultiPaymentService
            from decimal import Decimal
            
            multi_payment_service = MultiPaymentService()
            
            # Crear el pago múltiple
            multi_payment = multi_payment_service.create_multi_payment(
                sale_id=sale['id'],
                user_id=user_id,
                total_amount=Decimal(str(sale['total_amount'])),
                notes=f"Pago múltiple para venta {sale['id']}"
            )
            
            # Validar y corregir montos de pagos múltiples
            total_payment_amount = sum(Decimal(str(p['amount'])) for p in multi_payments)
            sale_total = Decimal(str(sale['total_amount']))
            
            # Si el total de pagos excede el total de la venta, ajustar proporcionalmente
            if total_payment_amount > sale_total:
                logger.warning(f"Total de pagos ({total_payment_amount}) excede el total de la venta ({sale_total}). Ajustando proporcionalmente.")
                adjustment_factor = sale_total / total_payment_amount
                for payment in multi_payments:
                    payment['amount'] = float(Decimal(str(payment['amount'])) * adjustment_factor)
            
            # Agregar cada detalle de pago
            for payment in multi_payments:
                multi_payment_service.add_payment(
                    multi_payment_id=multi_payment.id,
                    payment_method=payment['method'],
                    amount=Decimal(str(payment['amount'])),
                    reference=payment.get('reference'),
                    bank_name=payment.get('bank_name'),
                    card_last_four=payment.get('card_last_four'),
                    phone_number=payment.get('phone_number'),
                    qr_code=payment.get('qr_code'),
                    notes=payment.get('notes')
                )
            
            # Actualizar la venta con el ID del pago múltiple
            sale['multi_payment_id'] = multi_payment.id
            sale['is_multi_payment'] = True
        
        logger.info(f"Sale created: {sale['id']}", extra={
            'sale_id': sale['id'],
            'user_id': user_id,
            'total_amount': sale['total_amount']
        })
        
        return jsonify({
            'status': 'success',
            'data': sale,
            'message': 'Sale created successfully'
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error in create_sale: {e.message}", extra={
            'field': getattr(e, 'field', None),
            'context': e.context
        })
        return jsonify(e.to_dict()), e.status_code
    
    except BusinessLogicError as e:
        logger.warning(f"Business logic error in create_sale: {e.message}", extra={
            'operation': e.context.get('operation'),
            'context': e.context
        })
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Unexpected error in create_sale: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@sales_bp.route('/sales', methods=['GET'])

def get_sales():
    """Obtener lista de ventas"""
    try:
        # Obtener parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Obtener filtros
        user_id = request.args.get('user_id', type=int)
        status = request.args.get('status')
        
        # Obtener servicios
        sale_repository = container.get(SaleRepository)
        product_repository = container.get(ProductRepository)
        user_repository = container.get(UserRepository)
        
        sale_service = SaleService(sale_repository, product_repository, user_repository)
        
        # Aplicar filtros
        filters = {}
        if user_id:
            filters['user_id'] = user_id
        if status:
            filters['status'] = status
        
        # Obtener ventas
        result = sale_service.get_sales(page=page, per_page=per_page, **filters)
        
        return jsonify({
            'status': 'success',
            'data': {
                'sales': [sale.to_dict() for sale in result['items']],
                'pagination': result['pagination']
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_sales: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@sales_bp.route('/sales/<int:sale_id>', methods=['GET'])

def get_sale(sale_id):
    """Obtener venta por ID"""
    try:
        # Obtener servicios
        sale_repository = container.get(SaleRepository)
        product_repository = container.get(ProductRepository)
        user_repository = container.get(UserRepository)
        
        sale_service = SaleService(sale_repository, product_repository, user_repository)
        
        # Obtener venta
        sale = sale_service.get_sale(sale_id)
        
        return jsonify({
            'status': 'success',
            'data': sale
        })
        
    except Exception as e:
        logger.error(f"Error in get_sale: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@sales_bp.route('/sales/<int:sale_id>/cancel', methods=['POST'])

def cancel_sale(sale_id):
    """Cancelar venta"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Cancelled by user')
        
        # Obtener servicios
        sale_repository = container.get(SaleRepository)
        product_repository = container.get(ProductRepository)
        user_repository = container.get(UserRepository)
        
        sale_service = SaleService(sale_repository, product_repository, user_repository)
        
        # Cancelar venta
        sale = sale_service.cancel_sale(sale_id, reason)
        
        logger.info(f"Sale cancelled: {sale_id}", extra={
            'sale_id': sale_id,
            'reason': reason
        })
        
        return jsonify({
            'status': 'success',
            'data': sale,
            'message': 'Sale cancelled successfully'
        })
        
    except BusinessLogicError as e:
        logger.warning(f"Business logic error in cancel_sale: {e.message}", extra={
            'sale_id': sale_id,
            'operation': e.context.get('operation')
        })
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Error in cancel_sale: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@sales_bp.route('/sales/stats', methods=['GET'])

def get_sales_stats():
    """Obtener estadísticas de ventas"""
    try:
        user_id = request.args.get('user_id', type=int)
        
        # Obtener servicios
        sale_repository = container.get(SaleRepository)
        product_repository = container.get(ProductRepository)
        user_repository = container.get(UserRepository)
        
        sale_service = SaleService(sale_repository, product_repository, user_repository)
        
        # Obtener estadísticas
        stats = sale_service.get_sales_stats(user_id)
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error in get_sales_stats: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500
