"""
Inventory API Endpoints - Sistema POS O'Data
============================================
Endpoints para manejo de movimientos de inventario.
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.inventory import InventoryMovement
from app.models.product import Product
from app.models.user import User
from app.services.auth_service import token_required
from app.repositories.base_repository import BaseRepository
from datetime import datetime
from typing import Dict, Any, List
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint
inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/v1/inventory')

# Repositorios
inventory_repository = BaseRepository(InventoryMovement)
product_repository = BaseRepository(Product)
user_repository = BaseRepository(User)

@inventory_bp.route('/movements', methods=['GET'])
@token_required
def get_movements(current_user):
    """Obtener movimientos de inventario"""
    try:
        # Parámetros de consulta
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        movement_type = request.args.get('type')
        product_id = request.args.get('product_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Construir consulta
        query = InventoryMovement.query
        
        # Filtros
        if movement_type:
            query = query.filter(InventoryMovement.movement_type == movement_type)
        if product_id:
            query = query.filter(InventoryMovement.product_id == product_id)
        if date_from:
            query = query.filter(InventoryMovement.created_at >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(InventoryMovement.created_at <= datetime.fromisoformat(date_to))
        
        # Ordenar por fecha descendente
        query = query.order_by(InventoryMovement.created_at.desc())
        
        # Paginación
        movements = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Preparar respuesta
        movements_data = []
        for movement in movements.items:
            movement_dict = movement.to_dict()
            # Agregar información del producto
            product = Product.query.get(movement.product_id)
            if product:
                movement_dict['product_name'] = product.name
                movement_dict['product_sku'] = product.sku
            # Agregar información del usuario
            if movement.user_id:
                user = User.query.get(movement.user_id)
                if user:
                    movement_dict['user_name'] = user.username
            movements_data.append(movement_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'movements': movements_data,
                'pagination': {
                    'page': movements.page,
                    'pages': movements.pages,
                    'per_page': movements.per_page,
                    'total': movements.total,
                    'has_next': movements.has_next,
                    'has_prev': movements.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo movimientos: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@inventory_bp.route('/movements', methods=['POST'])
@token_required
def create_movement(current_user):
    """Crear movimiento de inventario"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['product_id', 'movement_type', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        product_id = data['product_id']
        movement_type = data['movement_type']
        quantity = data['quantity']
        reason = data.get('reason', 'Movimiento manual')
        notes = data.get('notes', '')
        location = data.get('location', 'main')
        
        # Validar que el producto existe
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'success': False,
                'message': 'Producto no encontrado'
            }), 404
        
        # Validar tipos de movimiento permitidos
        allowed_types = ['purchase', 'sale', 'adjustment', 'transfer', 'return', 'loss']
        if movement_type not in allowed_types:
            return jsonify({
                'success': False,
                'message': f'Tipo de movimiento no válido. Permitidos: {", ".join(allowed_types)}'
            }), 400
        
        # Para movimientos de venta, validar stock suficiente
        if movement_type == 'sale' and quantity > 0:
            if product.stock < quantity:
                return jsonify({
                    'success': False,
                    'message': f'Stock insuficiente. Disponible: {product.stock}, Solicitado: {quantity}'
                }), 400
        
        # Crear movimiento
        movement = InventoryMovement(
            product_id=product_id,
            movement_type=movement_type,
            quantity=quantity,
            reason=reason,
            user_id=current_user.id,
            notes=notes,
            location=location
        )
        
        # Actualizar stock del producto
        old_stock = product.stock
        product.stock += quantity
        
        # Validar que el stock no sea negativo
        if product.stock < 0:
            product.stock = old_stock  # Revertir cambio
            return jsonify({
                'success': False,
                'message': 'El stock no puede ser negativo'
            }), 400
        
        # Actualizar campos del movimiento
        movement.previous_stock = old_stock
        movement.new_stock = product.stock
        
        # Guardar en base de datos
        db.session.add(movement)
        db.session.commit()
        
        logger.info(f"Movimiento creado: {movement_type} {quantity} unidades de {product.name}")
        
        return jsonify({
            'success': True,
            'message': 'Movimiento creado exitosamente',
            'data': {
                'movement': movement.to_dict(),
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'stock_before': old_stock,
                    'stock_after': product.stock
                }
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando movimiento: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@inventory_bp.route('/movements/<int:movement_id>', methods=['GET'])
@token_required
def get_movement(current_user, movement_id):
    """Obtener movimiento específico"""
    try:
        movement = InventoryMovement.query.get(movement_id)
        if not movement:
            return jsonify({
                'success': False,
                'message': 'Movimiento no encontrado'
            }), 404
        
        movement_dict = movement.to_dict()
        
        # Agregar información adicional
        product = Product.query.get(movement.product_id)
        if product:
            movement_dict['product_name'] = product.name
            movement_dict['product_sku'] = product.sku
        
        if movement.user_id:
            user = User.query.get(movement.user_id)
            if user:
                movement_dict['user_name'] = user.username
        
        return jsonify({
            'success': True,
            'data': movement_dict
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo movimiento: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@inventory_bp.route('/purchase', methods=['POST'])
@token_required
def create_purchase(current_user):
    """Crear compra (entrada de inventario)"""
    try:
        data = request.get_json()
        
        # Validar datos
        if 'items' not in data:
            return jsonify({
                'success': False,
                'message': 'Se requieren items para la compra'
            }), 400
        
        items = data['items']
        if not isinstance(items, list) or len(items) == 0:
            return jsonify({
                'success': False,
                'message': 'Items debe ser una lista no vacía'
            }), 400
        
        supplier = data.get('supplier', 'Proveedor no especificado')
        notes = data.get('notes', '')
        
        created_movements = []
        total_cost = 0
        
        # Procesar cada item
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            cost = item.get('cost', 0)
            
            if not product_id or quantity <= 0:
                continue
            
            # Validar producto
            product = Product.query.get(product_id)
            if not product:
                continue
            
            # Crear movimiento de compra
            movement = InventoryMovement(
                product_id=product_id,
                movement_type='purchase',
                quantity=quantity,
                reason=f'Compra de {supplier}',
                user_id=current_user.id,
                notes=notes,
                location='main'
            )
            
            # Actualizar stock
            old_stock = product.stock
            product.stock += quantity
            movement.previous_stock = old_stock
            movement.new_stock = product.stock
            
            # Actualizar costo si se proporciona
            if cost > 0:
                product.cost = cost
                if product.price > 0:
                    product.margin = ((product.price - product.cost) / product.cost * 100)
            
            db.session.add(movement)
            created_movements.append(movement.to_dict())
            total_cost += quantity * cost
        
        db.session.commit()
        
        logger.info(f"Compra creada por {current_user.username}: {len(items)} items, costo total: ${total_cost}")
        
        return jsonify({
            'success': True,
            'message': f'Compra procesada exitosamente',
            'data': {
                'movements': created_movements,
                'total_cost': total_cost,
                'items_count': len(items)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando compra: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@inventory_bp.route('/adjustment', methods=['POST'])
@token_required
def create_adjustment(current_user):
    """Crear ajuste de inventario"""
    try:
        data = request.get_json()
        
        product_id = data.get('product_id')
        new_stock = data.get('new_stock')
        reason = data.get('reason', 'Ajuste manual de inventario')
        notes = data.get('notes', '')
        
        if not product_id or new_stock is None:
            return jsonify({
                'success': False,
                'message': 'Se requieren product_id y new_stock'
            }), 400
        
        # Validar producto
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'success': False,
                'message': 'Producto no encontrado'
            }), 404
        
        # Calcular diferencia
        old_stock = product.stock
        quantity = new_stock - old_stock
        
        # Crear movimiento de ajuste
        movement = InventoryMovement(
            product_id=product_id,
            movement_type='adjustment',
            quantity=quantity,
            reason=reason,
            user_id=current_user.id,
            notes=notes,
            location='main'
        )
        
        # Actualizar stock
        product.stock = new_stock
        movement.previous_stock = old_stock
        movement.new_stock = new_stock
        
        db.session.add(movement)
        db.session.commit()
        
        logger.info(f"Ajuste creado por {current_user.username}: {product.name} de {old_stock} a {new_stock}")
        
        return jsonify({
            'success': True,
            'message': 'Ajuste de inventario creado exitosamente',
            'data': {
                'movement': movement.to_dict(),
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'stock_before': old_stock,
                    'stock_after': new_stock,
                    'adjustment': quantity
                }
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando ajuste: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

@inventory_bp.route('/report/stock', methods=['GET'])
@token_required
def stock_report(current_user):
    """Reporte de stock actual"""
    try:
        # Parámetros de consulta
        category = request.args.get('category')
        low_stock_only = request.args.get('low_stock_only', 'false').lower() == 'true'
        
        # Construir consulta
        query = Product.query.filter(Product.is_active == True)
        
        if category:
            query = query.filter(Product.category == category)
        
        if low_stock_only:
            query = query.filter(Product.stock <= Product.min_stock)
        
        products = query.all()
        
        # Preparar datos del reporte
        report_data = []
        total_products = 0
        low_stock_count = 0
        out_of_stock_count = 0
        total_value = 0
        
        for product in products:
            total_products += 1
            
            if product.stock <= 0:
                out_of_stock_count += 1
            elif product.stock <= product.min_stock:
                low_stock_count += 1
            
            product_value = product.stock * float(product.price)
            total_value += product_value
            
            report_data.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'category': product.category,
                'stock': product.stock,
                'min_stock': product.min_stock,
                'price': float(product.price),
                'value': product_value,
                'is_low_stock': product.is_low_stock(),
                'is_out_of_stock': product.is_out_of_stock(),
                'needs_reorder': product.needs_reorder()
            })
        
        return jsonify({
            'success': True,
            'data': {
                'products': report_data,
                'summary': {
                    'total_products': total_products,
                    'low_stock_count': low_stock_count,
                    'out_of_stock_count': out_of_stock_count,
                    'total_value': total_value,
                    'generated_at': datetime.utcnow().isoformat()
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error generando reporte de stock: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error interno del servidor',
            'error': str(e)
        }), 500

