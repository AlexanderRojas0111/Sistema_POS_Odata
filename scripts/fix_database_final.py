#!/usr/bin/env python3
"""
Fix Database Final - Sistema POS O'Data
======================================
Script para eliminar completamente el problema de la tabla customers fantasma.
"""

import os
import sys
import sqlite3
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def fix_database_final():
    """Eliminar tabla customers fantasma y recrear base de datos limpia"""
    print("🔧 Iniciando corrección final de base de datos...")
    
    # Eliminar archivo de base de datos existente
    db_files = ['pos_odata.db', 'instance/pos_odata.db', 'instance/pos_odata_dev.db']
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"🗑️  Eliminando {db_file}...")
            os.remove(db_file)
    
    # Eliminar directorio instance
    if os.path.exists('instance'):
        print("🗑️  Eliminando directorio instance...")
        import shutil
        shutil.rmtree('instance', ignore_errors=True)
    
    # Crear directorio instance
    os.makedirs('instance', exist_ok=True)
    
    # Crear base de datos SQLite limpia directamente
    print("🏗️  Creando base de datos SQLite limpia...")
    conn = sqlite3.connect('pos_odata.db')
    cursor = conn.cursor()
    
    # Crear tabla users
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            is_active BOOLEAN DEFAULT 1,
            is_admin BOOLEAN DEFAULT 0,
            role VARCHAR(20) DEFAULT 'cashier',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    ''')
    
    # Crear tabla products
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            sku VARCHAR(50) UNIQUE NOT NULL,
            barcode VARCHAR(50) UNIQUE,
            price DECIMAL(10,2) NOT NULL,
            cost DECIMAL(10,2) NOT NULL,
            margin DECIMAL(5,2),
            stock INTEGER DEFAULT 0,
            min_stock INTEGER DEFAULT 5,
            max_stock INTEGER,
            reorder_point INTEGER DEFAULT 10,
            category VARCHAR(50),
            brand VARCHAR(50),
            supplier VARCHAR(100),
            is_active BOOLEAN DEFAULT 1,
            is_digital BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear tabla sales
    cursor.execute('''
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            customer_id INTEGER,
            subtotal DECIMAL(10,2) NOT NULL,
            tax_amount DECIMAL(10,2) DEFAULT 0.0,
            discount_amount DECIMAL(10,2) DEFAULT 0.0,
            total_amount DECIMAL(10,2) NOT NULL,
            payment_method VARCHAR(20) DEFAULT 'cash',
            payment_reference VARCHAR(100),
            change_amount DECIMAL(10,2) DEFAULT 0.0,
            status VARCHAR(20) DEFAULT 'completed',
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Crear tabla sale_items
    cursor.execute('''
        CREATE TABLE sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL,
            total_price DECIMAL(10,2) NOT NULL,
            discount_amount DECIMAL(10,2) DEFAULT 0.0,
            discount_reason VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sale_id) REFERENCES sales (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Crear tabla inventory_movements
    cursor.execute('''
        CREATE TABLE inventory_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER,
            movement_type VARCHAR(20) NOT NULL,
            quantity INTEGER NOT NULL,
            reason VARCHAR(100),
            reference_id INTEGER,
            reference_type VARCHAR(20),
            previous_stock INTEGER NOT NULL,
            new_stock INTEGER NOT NULL,
            notes TEXT,
            location VARCHAR(50) DEFAULT 'main',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Crear índices
    print("📊 Creando índices...")
    cursor.execute('CREATE INDEX idx_users_username ON users(username)')
    cursor.execute('CREATE INDEX idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX idx_users_active ON users(is_active)')
    cursor.execute('CREATE INDEX idx_products_sku ON products(sku)')
    cursor.execute('CREATE INDEX idx_products_category ON products(category)')
    cursor.execute('CREATE INDEX idx_products_active ON products(is_active)')
    cursor.execute('CREATE INDEX idx_sales_user_id ON sales(user_id)')
    cursor.execute('CREATE INDEX idx_sales_created_at ON sales(created_at)')
    cursor.execute('CREATE INDEX idx_sale_items_sale_id ON sale_items(sale_id)')
    cursor.execute('CREATE INDEX idx_sale_items_product_id ON sale_items(product_id)')
    
    # Insertar datos de ejemplo
    print("👤 Creando usuario admin...")
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, first_name, last_name, role, is_admin)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('admin', 'admin@pos-odata.com', 'admin123', 'Administrador', 'Sistema', 'admin', 1))
    
    print("📦 Creando productos de ejemplo...")
    products = [
        ('Coca Cola 350ml', 'Bebida gaseosa', 2.50, 1.80, 100, 'Bebidas', 'COCA-350'),
        ('Pan Integral', 'Pan de trigo integral', 1.20, 0.80, 50, 'Panadería', 'PAN-INT'),
        ('Leche Entera 1L', 'Leche de vaca entera', 3.50, 2.80, 30, 'Lácteos', 'LECH-1L')
    ]
    
    for product in products:
        cursor.execute('''
            INSERT INTO products (name, description, price, cost, stock, category, sku)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', product)
    
    # Confirmar cambios
    conn.commit()
    conn.close()
    
    print("✅ Base de datos creada exitosamente!")
    print("📋 Información de acceso:")
    print("   • Usuario: admin")
    print("   • Contraseña: admin123")
    print("   • Email: admin@pos-odata.com")
    print("   • Base de datos: pos_odata.db (SQLite)")
    
    # Verificar que no hay tabla customers
    print("\n🔍 Verificando esquema...")
    conn = sqlite3.connect('pos_odata.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print(f"   Tablas creadas: {', '.join(tables)}")
    if 'customers' in tables:
        print("   ❌ ERROR: Tabla customers encontrada!")
        return False
    else:
        print("   ✅ Tabla customers NO encontrada - CORRECTO!")
        return True

if __name__ == '__main__':
    success = fix_database_final()
    if success:
        print("\n🎉 Corrección completada exitosamente!")
    else:
        print("\n❌ Error en la corrección!")
        sys.exit(1)
