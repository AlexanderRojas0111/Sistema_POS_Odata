"""
Simple Products API - Sistema POS O'Data
=======================================
Versión simplificada de endpoints de productos para deployment.
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.product import Product
from app.exceptions import ValidationError
import logging
import time

logger = logging.getLogger(__name__)

# Crear blueprint
simple_products_bp = Blueprint('simple_products', __name__)

@simple_products_bp.route('/simple/products', methods=['POST'])
def create_product():
    """Crear producto - versión simplificada"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("Request body is required")
        
        # Validar datos requeridos
        name = data.get('name')
        price = data.get('price')
        
        if not name or not price:
            raise ValidationError("name and price are required")
        
        # Generar SKU si no se proporciona
        sku = data.get('sku')
        if not sku:
            sku = f"PROD_{int(time.time())}"
        
        # Verificar si el SKU ya existe
        existing_product = Product.query.filter_by(sku=sku).first()
        if existing_product:
            raise ValidationError(f"SKU '{sku}' already exists", field="sku")
        
        # Crear producto
        product = Product(
            name=name,
            sku=sku,
            price=price,
            cost=data.get('cost', 0.0),
            stock=data.get('stock', 0),
            description=data.get('description'),
            category=data.get('category'),
            brand=data.get('brand')
        )
        
        db.session.add(product)
        db.session.commit()
        
        logger.info(f"Product created: {name} (SKU: {sku})")
        
        return jsonify({
            'status': 'success',
            'data': product.to_dict(),
            'message': 'Product created successfully'
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error in create_product: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Unexpected error in create_product: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@simple_products_bp.route('/simple/products', methods=['GET'])
def get_products():
    """Obtener productos - versión simplificada"""
    try:
        products = Product.query.all()
        return jsonify({
            'status': 'success',
            'data': [product.to_dict() for product in products]
        })
        
    except Exception as e:
        logger.error(f"Error in get_products: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@simple_products_bp.route('/simple/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Obtener producto por ID - versión simplificada"""
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Product not found'
                }
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': product.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error in get_product: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500
