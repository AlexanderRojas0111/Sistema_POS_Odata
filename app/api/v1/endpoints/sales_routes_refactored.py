"""
Endpoints de ventas refactorizados usando la nueva arquitectura de servicios
Implementa principios SOLID y separación de responsabilidades
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal
from datetime import datetime, timedelta

from app.services.sales.sales_service import SalesService, SaleRefundService
from app.services.inventory.stock_service import StockService
from app.services.inventory.inventory_service import InventoryService
from app.schemas import SaleResponse
from app.core.database import db
from app.core.rate_limiter import rate_limit_10_per_minute
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
bp = Blueprint('sales_refactored', __name__, url_prefix='/sales')

# Inicializar servicios
stock_service = StockService()
inventory_service = InventoryService()
sales_service = SalesService(stock_service, inventory_service)
refund_service = SaleRefundService(stock_service, inventory_service)

@bp.route('/', methods=['POST'])
@jwt_required()
@rate_limit_10_per_minute
def create_sale():
    """
    Crear una nueva venta usando la arquitectura refactorizada
    
    Body esperado:
    {
        "items": [
            {
                "product_id": 1,
                "quantity": 2,
                "unit_price": 10.50,
                "discount": 0.0
            }
        ],
        "payment_method": "cash",
        "total_amount": 21.00,
        "customer_id": 1,
        "metadata": {}
    }
    """
    try:
        # Obtener datos de la solicitud
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        # Obtener usuario autenticado
        current_user_id = get_jwt_identity()
        
        # Crear venta usando el servicio
        sale = sales_service.create_sale(data, current_user_id)
        
        # Confirmar transacción
        db.session.commit()
        
        # Retornar respuesta
        return jsonify({
            'success': True,
            'sale': SaleResponse.from_orm(sale).dict(),
            'message': f'Venta creada exitosamente: {sale.invoice_number}'
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        logger.warning(f"Error de validación en venta: {str(e)}")
        return jsonify({
            'error': 'Datos inválidos',
            'details': str(e)
        }), 400
        
    except RuntimeError as e:
        db.session.rollback()
        logger.warning(f"Error de stock en venta: {str(e)}")
        return jsonify({
            'error': 'Error de stock',
            'details': str(e)
        }), 409  # Conflict
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error inesperado creando venta: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': 'Por favor contacte al administrador'
        }), 500

@bp.route('/<int:sale_id>', methods=['GET'])
@jwt_required()
def get_sale(sale_id):
    """Obtener una venta específica"""
    try:
        sale = sales_service.get_sale(sale_id)
        if not sale:
            return jsonify({'error': 'Venta no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'sale': SaleResponse.from_orm(sale).dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo venta {sale_id}: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/daily', methods=['GET'])
@jwt_required()
def get_daily_sales():
    """Obtener ventas del día actual"""
    try:
        # Obtener fecha del query parameter o usar hoy
        date_str = request.args.get('date')
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = datetime.now().date()
        
        sales = sales_service.get_daily_sales(date)
        
        return jsonify({
            'success': True,
            'date': date.isoformat(),
            'sales_count': len(sales),
            'sales': [SaleResponse.from_orm(sale).dict() for sale in sales]
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Formato de fecha inválido',
            'details': 'Use formato YYYY-MM-DD'
        }), 400
        
    except Exception as e:
        logger.error(f"Error obteniendo ventas diarias: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/reports/period', methods=['GET'])
@jwt_required()
def get_sales_report():
    """
    Generar reporte de ventas para un período
    
    Query parameters:
    - start_date: Fecha de inicio (YYYY-MM-DD)
    - end_date: Fecha de fin (YYYY-MM-DD)
    """
    try:
        # Obtener fechas de los query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({
                'error': 'Fechas requeridas',
                'details': 'Proporcione start_date y end_date'
            }), 400
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Validar que la fecha de inicio sea anterior a la de fin
        if start_date >= end_date:
            return jsonify({
                'error': 'Rango de fechas inválido',
                'details': 'La fecha de inicio debe ser anterior a la fecha de fin'
            }), 400
        
        # Generar reporte
        report = sales_service.get_sales_report(start_date, end_date)
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Formato de fecha inválido',
            'details': 'Use formato YYYY-MM-DD'
        }), 400
        
    except Exception as e:
        logger.error(f"Error generando reporte de ventas: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/<int:sale_id>/refund', methods=['POST'])
@jwt_required()
def process_refund(sale_id):
    """
    Procesar devolución de una venta
    
    Body esperado:
    {
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
                "reason": "defective"
            }
        ],
        "notes": "Producto defectuoso"
    }
    """
    try:
        # Obtener datos de la solicitud
        data = request.get_json()
        if not data or 'items' not in data:
            return jsonify({'error': 'Datos de devolución requeridos'}), 400
        
        # Obtener usuario autenticado
        current_user_id = get_jwt_identity()
        
        # Procesar devolución
        refund_sale = refund_service.process_refund(
            sale_id=sale_id,
            refund_items=data['items'],
            user_id=current_user_id
        )
        
        # Confirmar transacción
        db.session.commit()
        
        return jsonify({
            'success': True,
            'refund': SaleResponse.from_orm(refund_sale).dict(),
            'message': f'Devolución procesada exitosamente: {refund_sale.invoice_number}'
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        logger.warning(f"Error de validación en devolución: {str(e)}")
        return jsonify({
            'error': 'Datos inválidos',
            'details': str(e)
        }), 400
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error procesando devolución: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/stock-check', methods=['POST'])
@jwt_required()
def check_stock_availability():
    """
    Verificar disponibilidad de stock para múltiples productos
    
    Body esperado:
    {
        "items": [
            {
                "product_id": 1,
                "quantity": 2
            }
        ]
    }
    """
    try:
        data = request.get_json()
        if not data or 'items' not in data:
            return jsonify({'error': 'Items requeridos'}), 400
        
        stock_check_results = []
        overall_available = True
        
        for item in data['items']:
            product_id = item['product_id']
            quantity = Decimal(str(item['quantity']))
            
            available_stock = stock_service.get_available_stock(product_id)
            is_available = stock_service.is_stock_available(product_id, quantity)
            
            if not is_available:
                overall_available = False
            
            stock_check_results.append({
                'product_id': product_id,
                'requested_quantity': float(quantity),
                'available_stock': float(available_stock),
                'is_available': is_available,
                'shortage': float(max(Decimal('0'), quantity - available_stock))
            })
        
        return jsonify({
            'success': True,
            'overall_available': overall_available,
            'items': stock_check_results
        }), 200
        
    except Exception as e:
        logger.error(f"Error verificando stock: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/analytics/top-products', methods=['GET'])
@jwt_required()
def get_top_selling_products():
    """
    Obtener productos más vendidos en un período
    
    Query parameters:
    - days: Días hacia atrás (default: 30)
    - limit: Número de productos a retornar (default: 10)
    """
    try:
        days = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 10))
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Esta consulta requeriría unir con SaleItem para obtener productos vendidos
        # Por simplicidad, retornamos estructura de ejemplo
        
        return jsonify({
            'success': True,
            'period_days': days,
            'top_products': [
                {
                    'product_id': 1,
                    'product_name': 'Producto Ejemplo',
                    'total_sold': 100,
                    'total_revenue': 1500.00
                }
                # En implementación real, hacer query a SaleItem
            ]
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Parámetros inválidos',
            'details': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error obteniendo productos top: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# Error handlers específicos para este blueprint
@bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Método no permitido'}), 405
