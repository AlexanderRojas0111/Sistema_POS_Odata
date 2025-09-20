#!/usr/bin/env python3
"""
Reset Database - Sistema POS O'Data
===================================
Script para recrear la base de datos con el esquema correcto.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models import User, Product, Sale, SaleItem, InventoryMovement

def reset_database():
    """Recrear base de datos con esquema correcto"""
    print("🔄 Iniciando reset de base de datos...")
    
    # Crear aplicación
    app = create_app('production')
    
    with app.app_context():
        # Eliminar todas las tablas
        print("🗑️  Eliminando tablas existentes...")
        db.drop_all()
        
        # Crear todas las tablas
        print("🏗️  Creando esquema de base de datos...")
        db.create_all()
        
        # Verificar que las tablas se crearon correctamente
        print("✅ Verificando esquema...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['users', 'products', 'sales', 'sale_items', 'inventory_movements']
        for table in expected_tables:
            if table in tables:
                print(f"   ✅ Tabla {table} creada correctamente")
            else:
                print(f"   ❌ Tabla {table} NO encontrada")
        
        # Crear usuario admin por defecto
        print("👤 Creando usuario admin por defecto...")
        try:
            admin_user = User(
                username='admin',
                email='admin@pos-odata.com',
password=os.environ.get('DATABASE_PASSWORD', 'dev-password'),
                first_name='Administrador',
                last_name='Sistema',
                role='admin',
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("   ✅ Usuario admin creado: admin/admin123")
        except Exception as e:
            print(f"   ❌ Error creando usuario admin: {e}")
        
        # Crear productos de ejemplo
        print("📦 Creando productos de ejemplo...")
        try:
            sample_products = [
                {
                    'name': 'Coca Cola 350ml',
                    'description': 'Bebida gaseosa',
                    'price': 2.50,
                    'cost': 1.80,
                    'stock': 100,
                    'category': 'Bebidas',
                    'sku': 'COCA-350'
                },
                {
                    'name': 'Pan Integral',
                    'description': 'Pan de trigo integral',
                    'price': 1.20,
                    'cost': 0.80,
                    'stock': 50,
                    'category': 'Panadería',
                    'sku': 'PAN-INT'
                },
                {
                    'name': 'Leche Entera 1L',
                    'description': 'Leche de vaca entera',
                    'price': 3.50,
                    'cost': 2.80,
                    'stock': 30,
                    'category': 'Lácteos',
                    'sku': 'LECH-1L'
                }
            ]
            
            for product_data in sample_products:
                product = Product(**product_data)
                db.session.add(product)
            
            db.session.commit()
            print(f"   ✅ {len(sample_products)} productos de ejemplo creados")
        except Exception as e:
            print(f"   ❌ Error creando productos: {e}")
        
        print("🎉 Reset de base de datos completado exitosamente!")
        print("\n📋 Información de acceso:")
        print("   • Usuario: admin")
        print("   • Contraseña: admin123")
        print("   • Email: admin@pos-odata.com")

if __name__ == '__main__':
    reset_database()
