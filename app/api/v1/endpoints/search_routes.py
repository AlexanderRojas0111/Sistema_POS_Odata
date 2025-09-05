#!/usr/bin/env python3
"""
Rutas de Búsqueda - O'Data v2.0.0
==================================

Endpoints para:
- Búsqueda de productos
- Búsqueda de ventas
- Búsqueda de usuarios
- Filtros avanzados
- Búsqueda semántica básica

Autor: Sistema POS Odata
Versión: 2.0.0
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('search', __name__, url_prefix='/search')

@bp.route('/products', methods=['GET'])
def search_products():
    """
    Búsqueda de productos
    ---
    tags:
      - Búsqueda
    parameters:
      - name: q
        in: query
        type: string
        description: Término de búsqueda
      - name: category
        in: query
        type: string
        description: Categoría del producto
      - name: min_price
        in: query
        type: number
        description: Precio mínimo
      - name: max_price
        in: query
        type: number
        description: Precio máximo
      - name: in_stock
        in: query
        type: boolean
        description: Solo productos en stock
    responses:
      200:
        description: Resultados de búsqueda
    """
    try:
        # Importar modelos y base de datos dentro de la función
        from app import db
        from app.models.product import Product
        from app.models.inventory import Inventory
        
        # Parámetros de búsqueda
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        in_stock = request.args.get('in_stock', type=bool)
        
        # Construir consulta base
        products_query = Product.query
        
        # Aplicar filtros
        if query:
            products_query = products_query.filter(
                or_(
                    Product.name.ilike(f'%{query}%'),
                    Product.description.ilike(f'%{query}%'),
                    Product.category.ilike(f'%{query}%')
                )
            )
        
        if category:
            products_query = products_query.filter(Product.category.ilike(f'%{category}%'))
        
        if min_price is not None:
            products_query = products_query.filter(Product.price >= min_price)
        
        if max_price is not None:
            products_query = products_query.filter(Product.price <= max_price)
        
        if in_stock:
            products_query = products_query.join(Inventory).filter(Inventory.quantity > 0)
        
        # Ejecutar consulta
        products = products_query.limit(50).all()
        
        results = []
        for product in products:
            product_dict = product.to_dict()
            # Agregar información de inventario si está disponible
            try:
                inventory = Inventory.query.filter_by(product_id=product.id).first()
                if inventory:
                    product_dict['stock'] = inventory.quantity
                else:
                    product_dict['stock'] = 0
            except:
                product_dict['stock'] = 0
            
            results.append(product_dict)
        
        return jsonify({
            'query': query,
            'filters': {
                'category': category,
                'min_price': min_price,
                'max_price': max_price,
                'in_stock': in_stock
            },
            'total_results': len(results),
            'products': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error en búsqueda de productos: {e}")
        return jsonify({'error': 'Error en búsqueda'}), 500

@bp.route('/sales', methods=['GET'])
def search_sales():
    """
    Búsqueda de ventas
    ---
    tags:
      - Búsqueda
    parameters:
      - name: start_date
        in: query
        type: string
        description: Fecha de inicio (YYYY-MM-DD)
      - name: end_date
        in: query
        type: string
        description: Fecha de fin (YYYY-MM-DD)
      - name: min_amount
        in: query
        type: number
        description: Monto mínimo
      - name: max_amount
        in: query
        type: number
        description: Monto máximo
      - name: user_id
        in: query
        type: integer
        description: ID del usuario
    responses:
      200:
        description: Resultados de búsqueda
    """
    try:
        # Importar modelos y base de datos dentro de la función
        from app import db
        from app.models.sale import Sale
        from app.models.user import User
        
        # Parámetros de búsqueda
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        min_amount = request.args.get('min_amount', type=float)
        max_amount = request.args.get('max_amount', type=float)
        user_id = request.args.get('user_id', type=int)
        
        # Construir consulta base
        sales_query = Sale.query
        
        # Aplicar filtros de fecha
        if start_date:
            sales_query = sales_query.filter(Sale.created_at >= start_date)
        
        if end_date:
            sales_query = sales_query.filter(Sale.created_at <= end_date)
        
        # Aplicar filtros de monto
        if min_amount is not None:
            sales_query = sales_query.filter(Sale.total_amount >= min_amount)
        
        if max_amount is not None:
            sales_query = sales_query.filter(Sale.total_amount <= max_amount)
        
        # Aplicar filtro de usuario
        if user_id:
            sales_query = sales_query.filter(Sale.user_id == user_id)
        
        # Ejecutar consulta
        sales = sales_query.order_by(Sale.created_at.desc()).limit(50).all()
        
        results = []
        for sale in sales:
            sale_dict = sale.to_dict()
            # Agregar información del usuario si está disponible
            try:
                user = User.query.get(sale.user_id)
                if user:
                    sale_dict['user_name'] = user.username
                else:
                    sale_dict['user_name'] = 'Unknown'
            except:
                sale_dict['user_name'] = 'Unknown'
            
            results.append(sale_dict)
        
        return jsonify({
            'filters': {
                'start_date': start_date,
                'end_date': end_date,
                'min_amount': min_amount,
                'max_amount': max_amount,
                'user_id': user_id
            },
            'total_results': len(results),
            'sales': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error en búsqueda de ventas: {e}")
        return jsonify({'error': 'Error en búsqueda'}), 500

@bp.route('/users', methods=['GET'])
def search_users():
    """
    Búsqueda de usuarios
    ---
    tags:
      - Búsqueda
    parameters:
      - name: q
        in: query
        type: string
        description: Término de búsqueda
      - name: role
        in: query
        type: string
        description: Rol del usuario
      - name: active
        in: query
        type: boolean
        description: Solo usuarios activos
    responses:
      200:
        description: Resultados de búsqueda
    """
    try:
        # Importar modelos y base de datos dentro de la función
        from app import db
        from app.models.user import User
        
        # Parámetros de búsqueda
        query = request.args.get('q', '')
        role = request.args.get('role', '')
        active = request.args.get('active', type=bool)
        
        # Construir consulta base
        users_query = User.query
        
        # Aplicar filtros
        if query:
            users_query = users_query.filter(
                or_(
                    User.username.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%')
                )
            )
        
        if role:
            users_query = users_query.filter(User.role == role)
        
        if active is not None:
            users_query = users_query.filter(User.is_active == active)
        
        # Ejecutar consulta
        users = users_query.limit(50).all()
        
        results = []
        for user in users:
            user_dict = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
            results.append(user_dict)
        
        return jsonify({
            'query': query,
            'filters': {
                'role': role,
                'active': active
            },
            'total_results': len(results),
            'users': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error en búsqueda de usuarios: {e}")
        return jsonify({'error': 'Error en búsqueda'}), 500

@bp.route('/global', methods=['GET'])
def global_search():
    """
    Búsqueda global en todo el sistema
    ---
    tags:
      - Búsqueda
    parameters:
      - name: q
        in: query
        type: string
        required: true
        description: Término de búsqueda
      - name: limit
        in: query
        type: integer
        description: Límite de resultados por categoría
    responses:
      200:
        description: Resultados de búsqueda global
    """
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({'error': 'Término de búsqueda requerido'}), 400
        
        results = {
            'query': query,
            'products': [],
            'users': [],
            'sales': []
        }
        
        # Búsqueda en productos
        try:
            products = Product.query.filter(
                or_(
                    Product.name.ilike(f'%{query}%'),
                    Product.description.ilike(f'%{query}%'),
                    Product.category.ilike(f'%{query}%')
                )
            ).limit(limit).all()
            
            results['products'] = [product.to_dict() for product in products]
        except Exception as e:
            logger.error(f"Error buscando productos: {e}")
        
        # Búsqueda en usuarios
        try:
            users = User.query.filter(
                or_(
                    User.username.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%')
                )
            ).limit(limit).all()
            
            results['users'] = [{
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value
            } for user in users]
        except Exception as e:
            logger.error(f"Error buscando usuarios: {e}")
        
        # Búsqueda en ventas (por ID o monto)
        try:
            if query.isdigit():
                sales = Sale.query.filter(Sale.id == int(query)).limit(limit).all()
            else:
                sales = Sale.query.filter(Sale.total_amount >= float(query) if query.replace('.', '').isdigit() else False).limit(limit).all()
            
            results['sales'] = [sale.to_dict() for sale in sales]
        except Exception as e:
            logger.error(f"Error buscando ventas: {e}")
        
        # Calcular totales
        total_results = len(results['products']) + len(results['users']) + len(results['sales'])
        
        return jsonify({
            **results,
            'total_results': total_results
        }), 200
        
    except Exception as e:
        logger.error(f"Error en búsqueda global: {e}")
        return jsonify({'error': 'Error en búsqueda global'}), 500
