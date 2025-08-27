from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.core.database import db_session
from app.models.product import Product
from app.services.inventory.product_service import ProductService

bp = Blueprint('products', __name__, url_prefix='/products')
product_service = ProductService()

@bp.route('/', methods=['GET'])
def get_products():
    """Obtener lista de productos"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        
        with db_session() as session:
            query = session.query(Product)
            
            if category:
                query = query.filter(Product.category == category)
            
            products = query.paginate(page=page, per_page=per_page)
            
            return jsonify({
                'items': [product.to_dict() for product in products.items],
                'total': products.total,
                'pages': products.pages,
                'current_page': products.page
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Obtener un producto por ID"""
    try:
        with db_session() as session:
            product = session.query(Product).get(product_id)
            if product is None:
                return jsonify({'error': 'Product not found'}), 404
            return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
# @jwt_required()  # Temporalmente deshabilitado para setup inicial
def create_product():
    """Crear un nuevo producto"""
    try:
        data = request.get_json()
        with db_session() as session:
            product = Product(**data)
            session.add(product)
            session.commit()
            return jsonify(product.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """Actualizar un producto existente"""
    try:
        data = request.get_json()
        with db_session() as session:
            product = session.query(Product).get(product_id)
            if product is None:
                return jsonify({'error': 'Product not found'}), 404
            
            for key, value in data.items():
                setattr(product, key, value)
            
            session.commit()
            return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Eliminar un producto"""
    try:
        with db_session() as session:
            product = session.query(Product).get(product_id)
            if product is None:
                return jsonify({'error': 'Product not found'}), 404
            
            session.delete(product)
            session.commit()
            return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 400 