from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.sale import Sale, SaleItem
from app.models.product import Product
from app.core.database import db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

bp = Blueprint('sales', __name__, url_prefix='/ventas')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_sales():
    """
    Obtener todas las ventas
    ---
    tags:
      - Ventas
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        description: Número de página
      - name: per_page
        in: query
        type: integer
        description: Elementos por página
      - name: start_date
        in: query
        type: string
        format: date
        description: Fecha de inicio (YYYY-MM-DD)
      - name: end_date
        in: query
        type: string
        format: date
        description: Fecha de fin (YYYY-MM-DD)
    responses:
      200:
        description: Lista de ventas
        schema:
          type: object
          properties:
            sales:
              type: array
              items:
                $ref: '#/definitions/Sale'
            total:
              type: integer
            pages:
              type: integer
            current_page:
              type: integer
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Sale.query
        
        # Filtrar por fechas si se proporcionan
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(Sale.sale_date >= start_dt)
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
                
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(Sale.sale_date <= end_dt)
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        
        sales = query.order_by(Sale.sale_date.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'sales': [sale.to_dict() for sale in sales.items],
            'total': sales.total,
            'pages': sales.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo ventas: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/<int:sale_id>', methods=['GET'])
@jwt_required()
def get_sale(sale_id):
    """
    Obtener una venta específica
    ---
    tags:
      - Ventas
    parameters:
      - name: sale_id
        in: path
        type: integer
        required: true
        description: ID de la venta
    security:
      - Bearer: []
    responses:
      200:
        description: Venta encontrada
        schema:
          $ref: '#/definitions/Sale'
      404:
        description: Venta no encontrada
    """
    try:
        sale = Sale.query.get_or_404(sale_id)
        return jsonify(sale.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo venta {sale_id}: {e}")
        return jsonify({'error': 'Venta no encontrada'}), 404

@bp.route('/', methods=['POST'])
@jwt_required()
def create_sale():
    """
    Crear una nueva venta
    ---
    tags:
      - Ventas
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - products
          properties:
            products:
              type: array
              items:
                type: object
                required:
                  - product_id
                  - quantity
                properties:
                  product_id:
                    type: integer
                    description: ID del producto
                  quantity:
                    type: integer
                    description: Cantidad vendida
            customer_name:
              type: string
              description: Nombre del cliente
            payment_method:
              type: string
              description: Método de pago
    responses:
      201:
        description: Venta creada exitosamente
      400:
        description: Datos inválidos
      409:
        description: Stock insuficiente
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('products'):
            return jsonify({'error': 'Lista de productos es requerida'}), 400
        
        products_data = data['products']
        if not isinstance(products_data, list) or len(products_data) == 0:
            return jsonify({'error': 'Debe incluir al menos un producto'}), 400
        
        # Validar productos y stock
        total_amount = 0
        sale_items = []
        
        for item_data in products_data:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity', 1)
            
            if not product_id or not quantity:
                return jsonify({'error': 'product_id y quantity son requeridos'}), 400
            
            product = Product.query.get(product_id)
            if not product:
                return jsonify({'error': f'Producto {product_id} no encontrado'}), 404
            
            if product.stock < quantity:
                return jsonify({
                    'error': f'Stock insuficiente para {product.name}. Solicitado: {quantity}, Disponible: {product.stock}'
                }), 409
            
            # Calcular subtotal
            subtotal = product.price * quantity
            total_amount += subtotal
            
            # Crear item de venta
            sale_item = SaleItem(
                product_id=product_id,
                quantity=quantity,
                unit_price=product.price,
                subtotal=subtotal
            )
            sale_items.append(sale_item)
            
            # Actualizar stock
            product.stock -= quantity
        
        # Crear la venta
        sale = Sale(
            user_id=current_user_id,
            customer_name=data.get('customer_name', 'Cliente General'),
            total_amount=total_amount,
            payment_method=data.get('payment_method', 'Efectivo'),
            sale_date=datetime.utcnow()
        )
        
        # Agregar items a la venta
        sale.items = sale_items
        
        db.session.add(sale)
        db.session.commit()
        
        logger.info(f"Venta creada: ID {sale.id}, Total: ${total_amount}")
        return jsonify(sale.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando venta: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/<int:sale_id>', methods=['DELETE'])
@jwt_required()
def delete_sale(sale_id):
    """
    Eliminar una venta (solo si es reciente)
    ---
    tags:
      - Ventas
    parameters:
      - name: sale_id
        in: path
        type: integer
        required: true
        description: ID de la venta
    responses:
      200:
        description: Venta eliminada
      404:
        description: Venta no encontrada
      400:
        description: No se puede eliminar ventas antiguas
    """
    try:
        sale = Sale.query.get_or_404(sale_id)
        
        # Solo permitir eliminar ventas del mismo día
        if sale.sale_date.date() != datetime.utcnow().date():
            return jsonify({'error': 'Solo se pueden eliminar ventas del día actual'}), 400
        
        # Restaurar stock
        for item in sale.items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock += item.quantity
        
        db.session.delete(sale)
        db.session.commit()
        
        logger.info(f"Venta eliminada: ID {sale_id}")
        return jsonify({'message': f'Venta {sale_id} eliminada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando venta {sale_id}: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_sales_stats():
    """
    Obtener estadísticas de ventas
    ---
    tags:
      - Ventas
    security:
      - Bearer: []
    responses:
      200:
        description: Estadísticas de ventas
        schema:
          type: object
          properties:
            total_sales:
              type: integer
            total_revenue:
              type: number
            average_sale:
              type: number
            top_products:
              type: array
              items:
                type: object
                properties:
                  product_name:
                    type: string
                  total_sold:
                    type: integer
                  revenue:
                    type: number
    """
    try:
        # Estadísticas básicas
        total_sales = Sale.query.count()
        total_revenue = db.session.query(db.func.sum(Sale.total_amount)).scalar() or 0
        average_sale = total_revenue / total_sales if total_sales > 0 else 0
        
        # Productos más vendidos
        top_products = db.session.query(
            Product.name,
            db.func.sum(SaleItem.quantity).label('total_sold'),
            db.func.sum(SaleItem.subtotal).label('revenue')
        ).join(SaleItem).join(Sale).group_by(Product.id, Product.name)\
         .order_by(db.func.sum(SaleItem.quantity).desc()).limit(5).all()
        
        stats = {
            'total_sales': total_sales,
            'total_revenue': float(total_revenue),
            'average_sale': float(average_sale),
            'top_products': [
                {
                    'product_name': p[0],
                    'total_sold': p[1],
                    'revenue': float(p[2])
                }
                for p in top_products
            ]
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
