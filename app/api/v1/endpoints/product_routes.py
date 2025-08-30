from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.product import Product
from app.core.database import db
from app.schemas import ProductSchema
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('products', __name__, url_prefix='/productos')

# Schemas para validación
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_products():
    """
    Obtener todos los productos
    ---
    tags:
      - Productos
    security:
      - Bearer: []
    responses:
      200:
        description: Lista de productos
        schema:
          type: array
          items:
            $ref: '#/definitions/Product'
      401:
        description: No autorizado
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        products = Product.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'products': [product.to_dict() for product in products.items],
            'total': products.total,
            'pages': products.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo productos: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """
    Obtener un producto específico
    ---
    tags:
      - Productos
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID del producto
    security:
      - Bearer: []
    responses:
      200:
        description: Producto encontrado
        schema:
          $ref: '#/definitions/Product'
      404:
        description: Producto no encontrado
    """
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo producto {product_id}: {e}")
        return jsonify({'error': 'Producto no encontrado'}), 404

@bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    """
    Crear un nuevo producto
    ---
    tags:
      - Productos
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
            - category
          properties:
            name:
              type: string
              description: Nombre del producto
            description:
              type: string
              description: Descripción del producto
            price:
              type: number
              description: Precio del producto
            category:
              type: string
              description: Categoría del producto
            stock:
              type: integer
              description: Stock disponible
    responses:
      201:
        description: Producto creado exitosamente
      400:
        description: Datos inválidos
    """
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data or not data.get('name') or not data.get('price'):
            return jsonify({'error': 'Nombre y precio son requeridos'}), 400
        
        # Crear nuevo producto
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            category=data.get('category', 'General'),
            stock=data.get('stock', 0)
        )
        
        db.session.add(product)
        db.session.commit()
        
        logger.info(f"Producto creado: {product.name}")
        return jsonify(product.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando producto: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    """
    Actualizar un producto existente
    ---
    tags:
      - Productos
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID del producto
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            price:
              type: number
            category:
              type: string
            stock:
              type: integer
    responses:
      200:
        description: Producto actualizado
      404:
        description: Producto no encontrado
    """
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        if data.get('name'):
            product.name = data['name']
        if data.get('description'):
            product.description = data['description']
        if data.get('price'):
            product.price = float(data['price'])
        if data.get('category'):
            product.category = data['category']
        if data.get('stock') is not None:
            product.stock = int(data['stock'])
        
        db.session.commit()
        
        logger.info(f"Producto actualizado: {product.name}")
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando producto {product_id}: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """
    Eliminar un producto
    ---
    tags:
      - Productos
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID del producto
    responses:
      200:
        description: Producto eliminado
      404:
        description: Producto no encontrado
    """
    try:
        product = Product.query.get_or_404(product_id)
        name = product.name
        
        db.session.delete(product)
        db.session.commit()
        
        logger.info(f"Producto eliminado: {name}")
        return jsonify({'message': f'Producto {name} eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando producto {product_id}: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500 