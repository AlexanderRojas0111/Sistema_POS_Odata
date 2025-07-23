from flask import Blueprint, request, jsonify
from app.crud.sales import get_all_sales, create_sale

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/', methods=['GET'])
def get_sales():
    sales = get_all_sales()
    return jsonify([s.to_dict() for s in sales])

@sales_bp.route('/', methods=['POST'])
def create_sale_route():
    data = request.json
    sale = create_sale(data)
    return jsonify(sale.to_dict()), 201