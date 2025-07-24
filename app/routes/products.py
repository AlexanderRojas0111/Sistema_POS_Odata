from flask import Blueprint, request, jsonify
from app.models import Product
from app.database import db

products = Blueprint('products', __name__)

@products.route('/api/products', methods=['GET'])
def get_products():
    """Obtiene todos los productos"""
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])

@products.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Obtiene un producto por su ID"""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@products.route('/api/products', methods=['POST'])
def create_product():
    """Crea un nuevo producto"""
    data = request.get_json()
    
    product = Product(
        name=data['name'],
        stock=data.get('stock', 0),
        price=data['price']
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify(product.to_dict()), 201

@products.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Actualiza un producto existente"""
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    product.name = data.get('name', product.name)
    product.stock = data.get('stock', product.stock)
    product.price = data.get('price', product.price)
    
    db.session.commit()
    
    return jsonify(product.to_dict())

@products.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Elimina un producto"""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    return '', 204