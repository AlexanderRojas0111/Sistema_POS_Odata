from flask import Blueprint, request, jsonify
from app.models import Inventory, Product
from app.database import db

inventory = Blueprint('inventory', __name__)

@inventory.route('/api/inventory', methods=['GET'])
def get_inventory():
    """Obtiene todos los movimientos de inventario"""
    movements = Inventory.query.all()
    return jsonify([movement.to_dict() for movement in movements])

@inventory.route('/api/inventory/<int:movement_id>', methods=['GET'])
def get_movement(movement_id):
    """Obtiene un movimiento de inventario por su ID"""
    movement = Inventory.query.get_or_404(movement_id)
    return jsonify(movement.to_dict())

@inventory.route('/api/inventory', methods=['POST'])
def create_movement():
    """Crea un nuevo movimiento de inventario"""
    data = request.get_json()
    
    # Verificar producto
    product = Product.query.get_or_404(data['product_id'])
    
    # Crear movimiento
    movement = Inventory(
        product_id=data['product_id'],
        quantity=data['quantity'],
        movement_type=data['movement_type'],
        user_id=data['user_id']
    )
    
    # Actualizar stock del producto
    if data['movement_type'] == 'entrada':
        product.stock += data['quantity']
    elif data['movement_type'] == 'salida':
        if product.stock < data['quantity']:
            return jsonify({'error': 'Stock insuficiente'}), 400
        product.stock -= data['quantity']
    
    db.session.add(movement)
    db.session.commit()
    
    return jsonify(movement.to_dict()), 201

@inventory.route('/api/inventory/low-stock', methods=['GET'])
def get_low_stock():
    """Obtiene productos con stock bajo"""
    threshold = request.args.get('threshold', 5, type=int)
    products = Product.query.filter(Product.stock <= threshold).all()
    return jsonify([product.to_dict() for product in products])