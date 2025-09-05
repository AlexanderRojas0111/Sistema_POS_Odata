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
from app.core.database import db
from app.core.rate_limiter import rate_limit_10_per_minute
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
bp = Blueprint('sales', __name__, url_prefix='/ventas')

# Inicializar servicios
stock_service = StockService()
inventory_service = InventoryService()
sales_service = SalesService(stock_service, inventory_service)
refund_service = SaleRefundService(stock_service, inventory_service)

@bp.route('/', methods=['POST'])
# @jwt_required()  # Temporalmente deshabilitado para pruebas
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
        
        # Obtener usuario autenticado (temporalmente hardcodeado para pruebas)
        current_user_id = 1  # get_jwt_identity()
        
        # Crear venta usando el servicio
        sale = sales_service.create_sale(data, current_user_id)
        
        # Confirmar transacción
        db.session.commit()
        
        # Retornar respuesta
        return jsonify({
            'success': True,
            'sale': sale.to_dict() if hasattr(sale, 'to_dict') else str(sale),
            'message': f'Venta creada exitosamente: {getattr(sale, "invoice_number", "N/A")}'
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
    """
    Obtener una venta específica por ID
    """
    try:
        sale = sales_service.get_sale_by_id(sale_id)
        if not sale:
            return jsonify({'error': 'Venta no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'sale': sale.to_dict() if hasattr(sale, 'to_dict') else str(sale)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo venta {sale_id}: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': 'Por favor contacte al administrador'
        }), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_sales():
    """
    Obtener lista de ventas con paginación
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        sales = sales_service.get_sales_paginated(page, per_page)
        
        return jsonify({
            'success': True,
            'sales': [sale.to_dict() if hasattr(sale, 'to_dict') else str(sale) for sale in sales.items],
            'total': sales.total,
            'pages': sales.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo ventas: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': 'Por favor contacte al administrador'
        }), 500

@bp.route('/<int:sale_id>/refund', methods=['POST'])
@jwt_required()
def refund_sale(sale_id):
    """
    Procesar reembolso de una venta
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
        
        refund = refund_service.process_refund(sale_id, data)
        
        return jsonify({
            'success': True,
            'refund': refund.to_dict() if hasattr(refund, 'to_dict') else str(refund),
            'message': 'Reembolso procesado exitosamente'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Datos inválidos',
            'details': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error procesando reembolso: {str(e)}")
        return jsonify({
            'error': 'Error interno del servidor',
            'details': 'Por favor contacte al administrador'
        }), 500
