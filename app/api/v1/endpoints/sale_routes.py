from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.crud.sales import sales_crud
from app.schemas import SaleCreate, SaleUpdate, SaleResponse
from app.core.database import db

bp = Blueprint('sales', __name__, url_prefix='/sales')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_sales():
    """Obtener todas las ventas"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sales = sales_crud.get_all(page=page, per_page=per_page)
        return jsonify([SaleResponse.from_orm(sale).dict() for sale in sales]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:sale_id>', methods=['GET'])
@jwt_required()
def get_sale(sale_id):
    """Obtener una venta específica"""
    try:
        sale = sales_crud.get(sale_id)
        if not sale:
            return jsonify({'error': 'Venta no encontrada'}), 404
        return jsonify(SaleResponse.from_orm(sale).dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_sale():
    """Crear una nueva venta"""
    try:
        data = request.get_json()
        sale_data = SaleCreate(**data)
        sale = sales_crud.create(sale_data)
        db.session.commit()
        return jsonify(SaleResponse.from_orm(sale).dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:sale_id>', methods=['PUT'])
@jwt_required()
def update_sale(sale_id):
    """Actualizar una venta"""
    try:
        data = request.get_json()
        sale_data = SaleUpdate(**data)
        sale = sales_crud.update(sale_id, sale_data)
        if not sale:
            return jsonify({'error': 'Venta no encontrada'}), 404
        db.session.commit()
        return jsonify(SaleResponse.from_orm(sale).dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:sale_id>', methods=['DELETE'])
@jwt_required()
def delete_sale(sale_id):
    """Eliminar una venta"""
    try:
        success = sales_crud.delete(sale_id)
        if not success:
            return jsonify({'error': 'Venta no encontrada'}), 404
        db.session.commit()
        return jsonify({'message': 'Venta eliminada correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/today', methods=['GET'])
@jwt_required()
def get_today_sales():
    """Obtener ventas del día"""
    try:
        sales = sales_crud.get_today_sales()
        return jsonify([SaleResponse.from_orm(sale).dict() for sale in sales]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reports/daily', methods=['GET'])
@jwt_required()
def get_daily_report():
    """Obtener reporte diario de ventas"""
    try:
        date = request.args.get('date')
        report = sales_crud.get_daily_report(date)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reports/monthly', methods=['GET'])
@jwt_required()
def get_monthly_report():
    """Obtener reporte mensual de ventas"""
    try:
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        report = sales_crud.get_monthly_report(year, month)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 