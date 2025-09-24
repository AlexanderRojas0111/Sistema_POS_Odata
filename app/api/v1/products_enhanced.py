"""
Products API Enhanced - Sistema POS O'Data
==========================================
Endpoints de productos con validaciones y respuestas consistentes.
"""

from flask import Blueprint, request
from app.container import container
from app.services.product_service import ProductService
from app.repositories.product_repository import ProductRepository
from app.utils.response_helpers import (
    success_response, error_response, created_response, 
    updated_response, not_found_response, paginated_response
)
from app.schemas.validation_schemas import product_schema
from app.middleware.validation_middleware import validate_json_data
from app.middleware.error_handler_enhanced import error_handler
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
products_enhanced_bp = Blueprint('products_enhanced', __name__)

@products_enhanced_bp.route('/products', methods=['POST'])
@validate_json_data(product_schema)
@error_handler
def create_product():
    """Crear nuevo producto"""
    data = request.validated_data
    
    # Obtener servicio del container
    product_repository = container.get(ProductRepository)
    product_service = ProductService(product_repository)
    
    # Crear producto
    product = product_service.create_product(data)
    
    logger.info(f"Product created: {product['name']}", extra={
        'product_id': product['id'],
        'sku': product['sku']
    })
    
    return created_response(
        data=product,
        message="Producto creado exitosamente"
    )

@products_enhanced_bp.route('/products', methods=['GET'])
@error_handler
def get_products():
    """Obtener lista de productos con paginación"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    # Obtener servicio del container
    product_repository = container.get(ProductRepository)
    product_service = ProductService(product_repository)
    
    # Obtener productos
    products, total = product_service.get_products_paginated(
        page=page, 
        per_page=per_page, 
        search=search, 
        category=category
    )
    
    return paginated_response(
        data=products,
        page=page,
        per_page=per_page,
        total=total,
        message="Productos obtenidos exitosamente"
    )

@products_enhanced_bp.route('/products/<int:product_id>', methods=['GET'])
@error_handler
def get_product(product_id):
    """Obtener producto por ID"""
    # Obtener servicio del container
    product_repository = container.get(ProductRepository)
    product_service = ProductService(product_repository)
    
    # Obtener producto
    product = product_service.get_product_by_id(product_id)
    
    if not product:
        return not_found_response("Producto")
    
    return success_response(
        data=product,
        message="Producto obtenido exitosamente"
    )

@products_enhanced_bp.route('/products/<int:product_id>', methods=['PUT'])
@validate_json_data(product_schema)
@error_handler
def update_product(product_id):
    """Actualizar producto"""
    data = request.validated_data
    
    # Obtener servicio del container
    product_repository = container.get(ProductRepository)
    product_service = ProductService(product_repository)
    
    # Actualizar producto
    product = product_service.update_product(product_id, data)
    
    if not product:
        return not_found_response("Producto")
    
    logger.info(f"Product updated: {product['name']}", extra={
        'product_id': product['id'],
        'sku': product['sku']
    })
    
    return updated_response(
        data=product,
        message="Producto actualizado exitosamente"
    )

@products_enhanced_bp.route('/products/<int:product_id>', methods=['DELETE'])
@error_handler
def delete_product(product_id):
    """Eliminar producto"""
    # Obtener servicio del container
    product_repository = container.get(ProductRepository)
    product_service = ProductService(product_repository)
    
    # Eliminar producto
    success = product_service.delete_product(product_id)
    
    if not success:
        return not_found_response("Producto")
    
    logger.info(f"Product deleted", extra={
        'product_id': product_id
    })
    
    return success_response(
        data=None,
        message="Producto eliminado exitosamente"
    )
