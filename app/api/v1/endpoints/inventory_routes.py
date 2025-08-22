from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.crud.inventory import inventory_crud
from app.schemas import InventoryCreate, InventoryUpdate, InventoryResponse
from app.core.database import db
from app.models.inventory import Inventory

bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_inventory():
    """Obtener todo el inventario con paginación mejorada"""
    try:
        # Parámetros de paginación
        cursor = request.args.get('cursor', type=int)
        limit = min(int(request.args.get('limit', 20)), 100)  # Máximo 100 items
        
        # Aplicar filtros de búsqueda
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        low_stock = request.args.get('low_stock', type=bool)
        
        # Construir query base
        query = inventory_crud.get_query()
        
        # Aplicar filtros
        if search:
            query = query.filter(
                db.or_(
                    Inventory.name.ilike(f'%{search}%'),
                    Inventory.description.ilike(f'%{search}%'),
                    Inventory.sku.ilike(f'%{search}%')
                )
            )
        
        if category:
            query = query.filter(Inventory.category == category)
        
        if low_stock:
            threshold = request.args.get('threshold', 10, type=int)
            query = query.filter(Inventory.quantity <= threshold)
        
        # Aplicar paginación con cursor
        if cursor:
            query = query.filter(Inventory.id > cursor)
        
        # Obtener items con límite + 1 para saber si hay más
        items = query.limit(limit + 1).all()
        has_more = len(items) > limit
        
        if has_more:
            items = items[:-1]  # Remover el item extra
            next_cursor = items[-1].id if items else None
        else:
            next_cursor = None
        
        # Cachear resultados
        cache_key = f"inventory_list:{hash(str(request.args))}"
        if current_app.cache_manager:
            current_app.cache_manager.set(cache_key, {
                'items': [InventoryResponse.from_orm(item).dict() for item in items],
                'has_more': has_more,
                'next_cursor': next_cursor
            }, ttl=300)  # 5 minutos
        
        return jsonify({
            'items': [InventoryResponse.from_orm(item).dict() for item in items],
            'has_more': has_more,
            'next_cursor': next_cursor,
            'total_returned': len(items)
        }), 200
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