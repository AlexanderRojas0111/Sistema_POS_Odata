"""
Products API v1 - Sistema POS O'Data
===================================
Endpoints de productos con validaciones enterprise.
"""

from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.container import container
from app.services.product_service import ProductService
from app.repositories.product_repository import ProductRepository
from app.exceptions import ValidationError, BusinessLogicError
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
products_bp = Blueprint('products', __name__)

# Configurar rate limiting
limiter = Limiter(key_func=get_remote_address)

@products_bp.route('/products', methods=['POST'])
@limiter.limit("20 per minute")
def create_product():
    """Crear nuevo producto"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("Request body is required")
        
        # Obtener servicio del container
        product_repository = container.get(ProductRepository)
        product_service = ProductService(product_repository)
        
        # Crear producto
        product = product_service.create_product(data)
        
        logger.info(f"Product created: {product['name']}", extra={
            'product_id': product['id'],
            'sku': product['sku']
        })
        
        return jsonify({
            'status': 'success',
            'data': product,
            'message': 'Product created successfully'
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error in create_product: {e.message}", extra={
            'field': getattr(e, 'field', None),
            'context': e.context
        })
        return jsonify(e.to_dict()), e.status_code
    
    except ValueError as e:
        logger.warning(f"Value error in create_product: {str(e)}")
        return jsonify({
            'error': {
                'code': 'BAD_REQUEST',
                'message': str(e)
            }
        }), 400
    
    except Exception as e:
        logger.error(f"Unexpected error in create_product: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@products_bp.route('/products', methods=['GET'])
@limiter.limit("200 per minute")
def get_products():
    """Obtener lista de productos"""
    try:
        # Obtener parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Obtener filtros
        category = request.args.get('category')
        is_active = request.args.get('is_active', type=bool)
        search = request.args.get('search')
        
        # Obtener servicio
        product_repository = container.get(ProductRepository)
        product_service = ProductService(product_repository)
        
        # Aplicar filtros
        filters = {}
        if category:
            filters['category'] = category
        if is_active is not None:
            filters['is_active'] = is_active
        
        # Obtener productos
        if search:
            result = product_repository.search_products(search, page=page, per_page=per_page)
            products = [product.to_dict() for product in result['items']]
            pagination = result['pagination']
        else:
            result = product_service.get_products(page=page, per_page=per_page, **filters)
            products = result['products']
            pagination = result['pagination']
        
        return jsonify({
            'status': 'success',
            'data': {
                'products': products,
                'pagination': pagination
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_products: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
@limiter.limit("200 per minute")
def get_product(product_id):
    """Obtener producto por ID"""
    try:
        # Obtener servicio
        product_repository = container.get(ProductRepository)
        product_service = ProductService(product_repository)
        
        # Obtener producto
        product = product_service.get_product(product_id)
        
        return jsonify({
            'status': 'success',
            'data': product
        })
        
    except Exception as e:
        logger.error(f"Error in get_product: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@products_bp.route('/products/low-stock', methods=['GET'])
@limiter.limit("50 per minute")
def get_low_stock_products():
    """Obtener productos con stock bajo"""
    try:
        # Obtener parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Obtener servicio
        product_repository = container.get(ProductRepository)
        product_service = ProductService(product_repository)
        
        # Obtener productos con stock bajo
        result = product_service.get_low_stock_products(page=page, per_page=per_page)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in get_low_stock_products: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@limiter.limit("20 per minute")
def update_product(product_id):
    """Actualizar producto existente"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("Request body is required")
        
        # Obtener servicio del container
        product_repository = container.get(ProductRepository)
        product_service = ProductService(product_repository)
        
        # Actualizar producto
        product = product_service.update_product(product_id, data)
        
        logger.info(f"Product updated: {product['name']}", extra={
            'product_id': product['id'],
            'sku': product['sku']
        })
        
        return jsonify({
            'status': 'success',
            'data': product,
            'message': 'Product updated successfully'
        }), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error in update_product: {e.message}", extra={
            'field': getattr(e, 'field', None),
            'context': e.context
        })
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Unexpected error in update_product: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@limiter.limit("20 per minute")
def delete_product(product_id):
    """Eliminar producto"""
    try:
        # Obtener servicio del container
        product_repository = container.get(ProductRepository)
        product_service = ProductService(product_repository)
        
        # Eliminar producto
        product_service.delete_product(product_id)
        
        logger.info(f"Product deleted: ID {product_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Product deleted successfully'
        }), 200
        
    except ValidationError as e:
        logger.warning(f"Validation error in delete_product: {e.message}", extra={
            'field': getattr(e, 'field', None),
            'context': e.context
        })
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Unexpected error in delete_product: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@products_bp.route('/products/stats', methods=['GET'])
@limiter.limit("50 per minute")
def get_product_stats():
    """Obtener estadísticas de productos"""
    try:
        # Obtener servicio
        product_repository = container.get(ProductRepository)
        product_service = ProductService(product_repository)
        
        # Obtener estadísticas
        stats = product_service.get_product_stats()
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error in get_product_stats: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500
