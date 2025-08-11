from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.crud.inventory import inventory_crud
from app.schemas import InventoryCreate, InventoryUpdate, InventoryResponse
from app.core.database import db

bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_inventory():
    """Obtener todo el inventario"""
    try:
        inventory = inventory_crud.get_all()
        return jsonify([InventoryResponse.from_orm(item).dict() for item in inventory]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:inventory_id>', methods=['GET'])
@jwt_required()
def get_inventory_item(inventory_id):
    """Obtener un item específico del inventario"""
    try:
        item = inventory_crud.get(inventory_id)
        if not item:
            return jsonify({'error': 'Item no encontrado'}), 404
        return jsonify(InventoryResponse.from_orm(item).dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_inventory_item():
    """Crear un nuevo item en el inventario"""
    try:
        data = request.get_json()
        inventory_data = InventoryCreate(**data)
        item = inventory_crud.create(inventory_data)
        db.session.commit()
        return jsonify(InventoryResponse.from_orm(item).dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:inventory_id>', methods=['PUT'])
@jwt_required()
def update_inventory_item(inventory_id):
    """Actualizar un item del inventario"""
    try:
        data = request.get_json()
        inventory_data = InventoryUpdate(**data)
        item = inventory_crud.update(inventory_id, inventory_data)
        if not item:
            return jsonify({'error': 'Item no encontrado'}), 404
        db.session.commit()
        return jsonify(InventoryResponse.from_orm(item).dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:inventory_id>', methods=['DELETE'])
@jwt_required()
def delete_inventory_item(inventory_id):
    """Eliminar un item del inventario"""
    try:
        success = inventory_crud.delete(inventory_id)
        if not success:
            return jsonify({'error': 'Item no encontrado'}), 404
        db.session.commit()
        return jsonify({'message': 'Item eliminado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock():
    """Obtener items con stock bajo"""
    try:
        threshold = request.args.get('threshold', 10, type=int)
        items = inventory_crud.get_low_stock(threshold)
        return jsonify([InventoryResponse.from_orm(item).dict() for item in items]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 