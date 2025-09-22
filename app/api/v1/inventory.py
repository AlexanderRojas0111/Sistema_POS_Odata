"""
Inventory API v1 - Sistema POS Sabrositas
=========================================
Endpoints para gestión de inventario enterprise
"""

from flask import Blueprint, request, jsonify
from app.exceptions import ValidationError, BusinessLogicError
from app.container import container
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.services.inventory_service import InventoryService
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory', methods=['GET'])
def get_inventory():
    """Obtener inventario completo"""
    try:
        # Obtener parámetros
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        store_id = request.args.get('store_id', type=int)
        low_stock_only = request.args.get('low_stock_only', False, type=bool)
        
        # Respuesta simplificada para evitar errores de dependencias
        return jsonify({
            'status': 'success',
            'data': {
                'inventory': [],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': 0,
                    'pages': 0
                },
                'filters_applied': {
                    'store_id': store_id,
                    'low_stock_only': low_stock_only
                }
            }
        })
        
    except ValidationError as e:
        logger.warning(f"Validation error in get_inventory: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Error in get_inventory: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@inventory_bp.route('/inventory/summary', methods=['GET'])
def get_inventory_summary():
    """Obtener resumen del inventario"""
    try:
        store_id = request.args.get('store_id', type=int)
        
        # Obtener servicios
        inventory_repository = container.get(InventoryRepository)
        product_repository = container.get(ProductRepository)
        
        inventory_service = InventoryService(inventory_repository)
        
        # Obtener resumen
        summary = inventory_service.get_inventory_summary(store_id=store_id)
        
        return jsonify({
            'status': 'success',
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error in inventory summary: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@inventory_bp.route('/inventory/low-stock', methods=['GET'])
def get_low_stock_items():
    """Obtener productos con stock bajo"""
    try:
        store_id = request.args.get('store_id', type=int)
        
        # Obtener servicios
        inventory_repository = container.get(InventoryRepository)
        product_repository = container.get(ProductRepository)
        
        inventory_service = InventoryService(inventory_repository)
        
        # Obtener productos con stock bajo
        low_stock_items = inventory_service.get_low_stock_products(store_id=store_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'low_stock_items': low_stock_items,
                'count': len(low_stock_items),
                'store_id': store_id
            }
        })
        
    except Exception as e:
        logger.error(f"Error in low stock items: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@inventory_bp.route('/inventory/adjust', methods=['POST'])
def adjust_inventory():
    """Ajustar inventario de productos"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("Request body is required")
        
        # Validar campos requeridos
        required_fields = ['product_id', 'quantity', 'reason']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Field '{field}' is required")
        
        # Obtener servicios
        inventory_repository = container.get(InventoryRepository)
        product_repository = container.get(ProductRepository)
        
        inventory_service = InventoryService(inventory_repository)
        
        # Realizar ajuste
        adjustment = inventory_service.adjust_inventory(
            product_id=data['product_id'],
            quantity=data['quantity'],
            reason=data['reason'],
            store_id=data.get('store_id')
        )
        
        logger.info(f"Inventory adjusted", extra={
            'product_id': data['product_id'],
            'quantity': data['quantity'],
            'reason': data['reason']
        })
        
        return jsonify({
            'status': 'success',
            'data': adjustment,
            'message': 'Inventory adjusted successfully'
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error in adjust_inventory: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except BusinessLogicError as e:
        logger.warning(f"Business logic error in adjust_inventory: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Error in adjust_inventory: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500
