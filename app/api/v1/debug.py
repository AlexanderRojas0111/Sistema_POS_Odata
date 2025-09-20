"""
Debug API - Sistema Sabrositas
==============================
Endpoints para debugging y limpieza del sistema
"""

from flask import Blueprint, jsonify
from app import db
from app.models.product import Product
from app.models.user import User
from app.models.sale import Sale
import sqlite3
import os

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug/database-status', methods=['GET'])
def database_status():
    """Verificar estado real de la base de datos"""
    try:
        # Verificar usando SQLAlchemy
        sqlalchemy_products = Product.query.count()
        sqlalchemy_users = User.query.count()
        
        # Verificar usando SQLite directo
        db_path = None
        if os.path.exists('instance/pos_odata.db'):
            db_path = 'instance/pos_odata.db'
        elif os.path.exists('pos_odata.db'):
            db_path = 'pos_odata.db'
        
        sqlite_data = {}
        if db_path:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute("SELECT COUNT(*) FROM products")
                sqlite_data['products'] = cursor.fetchone()[0]
            except:
                sqlite_data['products'] = 'table_not_exists'
            
            try:
                cursor.execute("SELECT COUNT(*) FROM users")
                sqlite_data['users'] = cursor.fetchone()[0]
            except:
                sqlite_data['users'] = 'table_not_exists'
            
            conn.close()
        
        return jsonify({
            'status': 'success',
            'data': {
                'database_path': db_path,
                'sqlalchemy_counts': {
                    'products': sqlalchemy_products,
                    'users': sqlalchemy_users
                },
                'sqlite_direct_counts': sqlite_data,
                'database_uri': db.engine.url.__str__()
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@debug_bp.route('/debug/clear-all-data', methods=['POST'])
def clear_all_data():
    """Limpiar TODOS los datos usando SQLAlchemy"""
    try:
        # Eliminar usando SQLAlchemy
        db.session.query(Sale).delete()
        db.session.query(Product).delete()
        db.session.query(User).delete()
        
        db.session.commit()
        
        # Verificar limpieza
        remaining_products = Product.query.count()
        remaining_users = User.query.count()
        
        return jsonify({
            'status': 'success',
            'message': 'Todos los datos eliminados via SQLAlchemy',
            'data': {
                'remaining_products': remaining_products,
                'remaining_users': remaining_users
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
