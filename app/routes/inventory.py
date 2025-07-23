from flask import Blueprint, request, jsonify
from app.crud.inventory import get_all_inventory, create_inventory

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    inventory = get_all_inventory()
    return jsonify([i.to_dict() for i in inventory])

@inventory_bp.route('/', methods=['POST'])
def create_inventory_route():
    data = request.json
    inventory = create_inventory(data)
    return jsonify(inventory.to_dict()), 201