from flask import Blueprint, request, jsonify
from app.crud.users import get_all_users, create_user

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
def get_users():
    users = get_all_users()
    return jsonify([u.to_dict() for u in users])

@users_bp.route('/', methods=['POST'])
def create_user_route():
    data = request.json
    user = create_user(data)
    return jsonify(user.to_dict()), 201