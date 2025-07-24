from flask import Blueprint, request, jsonify
from app.crud.customers import get_all_customers, create_customer

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/', methods=['GET'])
def get_customers():
    customers = get_all_customers()
    return jsonify([c.to_dict() for c in customers])

@customers_bp.route('/', methods=['POST'])
def create_customer_route():
    data = request.json
    customer = create_customer(data)
    return jsonify(customer.to_dict()), 201 