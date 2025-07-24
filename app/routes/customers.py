from flask import Blueprint, request, jsonify
from app.models import Customer
from app.database import db

customers = Blueprint('customers', __name__)

@customers.route('/api/customers', methods=['GET'])
def get_customers():
    """Obtiene todos los clientes"""
    customers = Customer.query.all()
    return jsonify([customer.to_dict() for customer in customers])

@customers.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Obtiene un cliente por su ID"""
    customer = Customer.query.get_or_404(customer_id)
    return jsonify(customer.to_dict())

@customers.route('/api/customers', methods=['POST'])
def create_customer():
    """Crea un nuevo cliente"""
    data = request.get_json()
    
    # Verificar si el email ya existe
    if data.get('email') and Customer.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El email ya está registrado'}), 400
    
    # Crear cliente
    customer = Customer(
        name=data['name'],
        email=data.get('email'),
        phone=data.get('phone')
    )
    
    db.session.add(customer)
    db.session.commit()
    
    return jsonify(customer.to_dict()), 201

@customers.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Actualiza un cliente existente"""
    customer = Customer.query.get_or_404(customer_id)
    data = request.get_json()
    
    # Verificar email único
    if 'email' in data:
        existing_customer = Customer.query.filter_by(email=data['email']).first()
        if existing_customer and existing_customer.id != customer_id:
            return jsonify({'error': 'El email ya está registrado'}), 400
        customer.email = data['email']
    
    if 'name' in data:
        customer.name = data['name']
    
    if 'phone' in data:
        customer.phone = data['phone']
    
    db.session.commit()
    return jsonify(customer.to_dict())

@customers.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Elimina un cliente"""
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return '', 204 