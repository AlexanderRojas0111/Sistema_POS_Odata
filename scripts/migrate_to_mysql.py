#!/usr/bin/env python3
"""
Script de Migración SQLite a MySQL - Sistema Multi-Sede Sabrositas
================================================================
Migra datos existentes de SQLite a MySQL con soporte multi-tienda.
"""

import sqlite3
import mysql.connector
import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.store import Store
from app.models.user import User
from app.models.product import Product

class SQLiteToMySQLMigrator:
    """Migrador de SQLite a MySQL para sistema multi-sede"""
    
    def __init__(self, sqlite_db_path: str, mysql_config: Dict[str, str]):
        self.sqlite_db_path = sqlite_db_path
        self.mysql_config = mysql_config
        self.sqlite_conn = None
        self.mysql_conn = None
        self.migration_log = []
    
    def connect_databases(self):
        """Conectar a ambas bases de datos"""
        try:
            # Conectar SQLite
            self.sqlite_conn = sqlite3.connect(self.sqlite_db_path)
            self.sqlite_conn.row_factory = sqlite3.Row
            print(f"✅ Conectado a SQLite: {self.sqlite_db_path}")
            
            # Conectar MySQL
            self.mysql_conn = mysql.connector.connect(**self.mysql_config)
            print(f"✅ Conectado a MySQL: {self.mysql_config['host']}:{self.mysql_config['port']}")
            
        except Exception as e:
            print(f"❌ Error conectando bases de datos: {e}")
            raise
    
    def create_mysql_schema(self):
        """Crear esquema MySQL para multi-sede"""
        cursor = self.mysql_conn.cursor()
        
        schema_sql = """
        -- Crear base de datos si no existe
        CREATE DATABASE IF NOT EXISTS sabrositas_pos_multistore 
        CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        
        USE sabrositas_pos_multistore;
        
        -- Tabla de tiendas
        CREATE TABLE IF NOT EXISTS stores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(10) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            address TEXT,
            phone VARCHAR(20),
            email VARCHAR(100),
            manager_id INT,
            region VARCHAR(50),
            store_type VARCHAR(20) DEFAULT 'retail',
            is_active BOOLEAN DEFAULT TRUE,
            is_main_store BOOLEAN DEFAULT FALSE,
            timezone VARCHAR(50) DEFAULT 'America/Bogota',
            max_concurrent_sales INT DEFAULT 10,
            auto_sync_inventory BOOLEAN DEFAULT TRUE,
            sync_frequency_minutes INT DEFAULT 15,
            tax_rate DECIMAL(5,4) DEFAULT 0.1900,
            currency VARCHAR(3) DEFAULT 'COP',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            last_sync_at TIMESTAMP NULL,
            INDEX idx_code (code),
            INDEX idx_is_active (is_active),
            INDEX idx_region (region)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
        -- Actualizar tabla de usuarios para multi-sede
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS assigned_store_id INT,
        ADD COLUMN IF NOT EXISTS can_access_all_stores BOOLEAN DEFAULT FALSE,
        ADD INDEX IF NOT EXISTS idx_assigned_store (assigned_store_id);
        
        -- Tabla de productos por tienda
        CREATE TABLE IF NOT EXISTS store_products (
            store_id INT NOT NULL,
            product_id INT NOT NULL,
            local_price DECIMAL(10,2) NOT NULL,
            cost_price DECIMAL(10,2),
            current_stock INT DEFAULT 0,
            min_stock INT DEFAULT 5,
            max_stock INT DEFAULT 100,
            reorder_point INT DEFAULT 10,
            is_available BOOLEAN DEFAULT TRUE,
            is_featured BOOLEAN DEFAULT FALSE,
            allow_negative_stock BOOLEAN DEFAULT FALSE,
            track_expiration BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            last_sale_at TIMESTAMP NULL,
            PRIMARY KEY (store_id, product_id),
            FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            INDEX idx_store_available (store_id, is_available),
            INDEX idx_low_stock (store_id, current_stock, min_stock)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
        -- Tabla de transferencias de inventario
        CREATE TABLE IF NOT EXISTS inventory_transfers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            transfer_number VARCHAR(20) UNIQUE NOT NULL,
            from_store_id INT NOT NULL,
            to_store_id INT NOT NULL,
            status ENUM('pending', 'approved', 'in_transit', 'delivered', 'cancelled', 'rejected') DEFAULT 'pending',
            transfer_type ENUM('manual', 'automatic', 'emergency', 'rebalance') DEFAULT 'manual',
            priority VARCHAR(10) DEFAULT 'normal',
            reason TEXT,
            notes TEXT,
            requested_by INT NOT NULL,
            approved_by INT,
            received_by INT,
            total_items INT DEFAULT 0,
            total_cost DECIMAL(12,2) DEFAULT 0.00,
            shipping_cost DECIMAL(10,2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP NULL,
            shipped_at TIMESTAMP NULL,
            delivered_at TIMESTAMP NULL,
            expected_delivery TIMESTAMP NULL,
            FOREIGN KEY (from_store_id) REFERENCES stores(id),
            FOREIGN KEY (to_store_id) REFERENCES stores(id),
            FOREIGN KEY (requested_by) REFERENCES users(id),
            FOREIGN KEY (approved_by) REFERENCES users(id),
            FOREIGN KEY (received_by) REFERENCES users(id),
            INDEX idx_transfer_number (transfer_number),
            INDEX idx_from_store (from_store_id),
            INDEX idx_to_store (to_store_id),
            INDEX idx_status (status),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
        -- Tabla de items de transferencia
        CREATE TABLE IF NOT EXISTS inventory_transfer_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            transfer_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            received_quantity INT,
            unit_cost DECIMAL(10,2) NOT NULL,
            total_cost DECIMAL(12,2) NOT NULL,
            condition VARCHAR(20) DEFAULT 'good',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transfer_id) REFERENCES inventory_transfers(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id),
            INDEX idx_transfer (transfer_id),
            INDEX idx_product (product_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        
        -- Agregar store_id a ventas si no existe
        ALTER TABLE sales 
        ADD COLUMN IF NOT EXISTS store_id INT,
        ADD INDEX IF NOT EXISTS idx_store_sales (store_id);
        
        -- Agregar store_id a movimientos de inventario si no existe
        ALTER TABLE inventory_movements 
        ADD COLUMN IF NOT EXISTS store_id INT,
        ADD INDEX IF NOT EXISTS idx_store_movements (store_id);
        """
        
        try:
            for statement in schema_sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)
            
            self.mysql_conn.commit()
            print("✅ Esquema MySQL creado exitosamente")
            self.migration_log.append("Schema MySQL creado")
            
        except Exception as e:
            print(f"❌ Error creando esquema MySQL: {e}")
            raise
        finally:
            cursor.close()
    
    def create_main_store(self) -> int:
        """Crear tienda principal para datos existentes"""
        cursor = self.mysql_conn.cursor()
        
        try:
            # Verificar si ya existe tienda principal
            cursor.execute("SELECT id FROM stores WHERE is_main_store = TRUE LIMIT 1")
            existing = cursor.fetchone()
            
            if existing:
                print(f"✅ Tienda principal ya existe: ID {existing[0]}")
                return existing[0]
            
            # Crear tienda principal
            store_data = {
                'code': 'MAIN001',
                'name': 'Sabrositas - Sede Principal',
                'address': 'Dirección Principal',
                'phone': '300-000-0000',
                'email': 'principal@sabrositas.com',
                'region': 'Bogotá',
                'store_type': 'retail',
                'is_active': True,
                'is_main_store': True,
                'timezone': 'America/Bogota',
                'tax_rate': 0.19,
                'currency': 'COP'
            }
            
            insert_sql = """
            INSERT INTO stores (code, name, address, phone, email, region, store_type, 
                              is_active, is_main_store, timezone, tax_rate, currency)
            VALUES (%(code)s, %(name)s, %(address)s, %(phone)s, %(email)s, %(region)s, 
                   %(store_type)s, %(is_active)s, %(is_main_store)s, %(timezone)s, 
                   %(tax_rate)s, %(currency)s)
            """
            
            cursor.execute(insert_sql, store_data)
            store_id = cursor.lastrowid
            
            self.mysql_conn.commit()
            print(f"✅ Tienda principal creada: ID {store_id}")
            self.migration_log.append(f"Tienda principal creada: ID {store_id}")
            
            return store_id
            
        except Exception as e:
            print(f"❌ Error creando tienda principal: {e}")
            raise
        finally:
            cursor.close()
    
    def migrate_users(self, main_store_id: int):
        """Migrar usuarios de SQLite a MySQL"""
        sqlite_cursor = self.sqlite_conn.cursor()
        mysql_cursor = self.mysql_conn.cursor()
        
        try:
            # Obtener usuarios de SQLite
            sqlite_cursor.execute("SELECT * FROM users")
            users = sqlite_cursor.fetchall()
            
            migrated_count = 0
            
            for user in users:
                try:
                    # Preparar datos del usuario
                    user_data = {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'password_hash': user['password_hash'],
                        'first_name': user.get('first_name'),
                        'last_name': user.get('last_name'),
                        'is_active': user.get('is_active', True),
                        'is_admin': user.get('is_admin', False),
                        'role': user.get('role', 'cashier'),
                        'assigned_store_id': main_store_id,  # Asignar a tienda principal
                        'can_access_all_stores': user.get('is_admin', False),  # Admins pueden acceder a todas
                        'created_at': user.get('created_at'),
                        'updated_at': user.get('updated_at'),
                        'last_login': user.get('last_login')
                    }
                    
                    # Insertar usuario en MySQL
                    insert_sql = """
                    INSERT INTO users (id, username, email, password_hash, first_name, last_name,
                                     is_active, is_admin, role, assigned_store_id, can_access_all_stores,
                                     created_at, updated_at, last_login)
                    VALUES (%(id)s, %(username)s, %(email)s, %(password_hash)s, %(first_name)s, 
                           %(last_name)s, %(is_active)s, %(is_admin)s, %(role)s, %(assigned_store_id)s,
                           %(can_access_all_stores)s, %(created_at)s, %(updated_at)s, %(last_login)s)
                    ON DUPLICATE KEY UPDATE
                    assigned_store_id = VALUES(assigned_store_id),
                    can_access_all_stores = VALUES(can_access_all_stores)
                    """
                    
                    mysql_cursor.execute(insert_sql, user_data)
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"⚠️ Error migrando usuario {user['username']}: {e}")
                    continue
            
            self.mysql_conn.commit()
            print(f"✅ Usuarios migrados: {migrated_count}")
            self.migration_log.append(f"Usuarios migrados: {migrated_count}")
            
        except Exception as e:
            print(f"❌ Error migrando usuarios: {e}")
            raise
        finally:
            sqlite_cursor.close()
            mysql_cursor.close()
    
    def migrate_products_to_store(self, main_store_id: int):
        """Migrar productos y crear relaciones con tienda principal"""
        sqlite_cursor = self.sqlite_conn.cursor()
        mysql_cursor = self.mysql_conn.cursor()
        
        try:
            # Obtener productos de SQLite
            sqlite_cursor.execute("SELECT * FROM products WHERE is_active = 1")
            products = sqlite_cursor.fetchall()
            
            migrated_count = 0
            
            for product in products:
                try:
                    # Crear relación producto-tienda
                    store_product_data = {
                        'store_id': main_store_id,
                        'product_id': product['id'],
                        'local_price': float(product['price']),
                        'cost_price': float(product.get('cost', 0)),
                        'current_stock': int(product.get('stock', 0)),
                        'min_stock': int(product.get('min_stock', 5)),
                        'max_stock': int(product.get('max_stock', 100)),
                        'reorder_point': int(product.get('reorder_point', 10)),
                        'is_available': True,
                        'is_featured': False,
                        'allow_negative_stock': False,
                        'track_expiration': True
                    }
                    
                    # Insertar en store_products
                    insert_sql = """
                    INSERT INTO store_products (store_id, product_id, local_price, cost_price,
                                              current_stock, min_stock, max_stock, reorder_point,
                                              is_available, is_featured, allow_negative_stock, track_expiration)
                    VALUES (%(store_id)s, %(product_id)s, %(local_price)s, %(cost_price)s,
                           %(current_stock)s, %(min_stock)s, %(max_stock)s, %(reorder_point)s,
                           %(is_available)s, %(is_featured)s, %(allow_negative_stock)s, %(track_expiration)s)
                    ON DUPLICATE KEY UPDATE
                    local_price = VALUES(local_price),
                    current_stock = VALUES(current_stock)
                    """
                    
                    mysql_cursor.execute(insert_sql, store_product_data)
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"⚠️ Error migrando producto {product['name']}: {e}")
                    continue
            
            self.mysql_conn.commit()
            print(f"✅ Productos migrados a tienda principal: {migrated_count}")
            self.migration_log.append(f"Productos migrados: {migrated_count}")
            
        except Exception as e:
            print(f"❌ Error migrando productos: {e}")
            raise
        finally:
            sqlite_cursor.close()
            mysql_cursor.close()
    
    def migrate_sales(self, main_store_id: int):
        """Migrar ventas asignándolas a la tienda principal"""
        sqlite_cursor = self.sqlite_conn.cursor()
        mysql_cursor = self.mysql_conn.cursor()
        
        try:
            # Actualizar ventas existentes con store_id
            mysql_cursor.execute(
                "UPDATE sales SET store_id = %s WHERE store_id IS NULL",
                (main_store_id,)
            )
            
            updated_count = mysql_cursor.rowcount
            self.mysql_conn.commit()
            
            print(f"✅ Ventas actualizadas con tienda principal: {updated_count}")
            self.migration_log.append(f"Ventas actualizadas: {updated_count}")
            
        except Exception as e:
            print(f"❌ Error migrando ventas: {e}")
            raise
        finally:
            sqlite_cursor.close()
            mysql_cursor.close()
    
    def migrate_inventory_movements(self, main_store_id: int):
        """Migrar movimientos de inventario asignándolos a la tienda principal"""
        mysql_cursor = self.mysql_conn.cursor()
        
        try:
            # Actualizar movimientos existentes con store_id
            mysql_cursor.execute(
                "UPDATE inventory_movements SET store_id = %s WHERE store_id IS NULL",
                (main_store_id,)
            )
            
            updated_count = mysql_cursor.rowcount
            self.mysql_conn.commit()
            
            print(f"✅ Movimientos de inventario actualizados: {updated_count}")
            self.migration_log.append(f"Movimientos actualizados: {updated_count}")
            
        except Exception as e:
            print(f"❌ Error migrando movimientos de inventario: {e}")
            raise
        finally:
            mysql_cursor.close()
    
    def run_migration(self):
        """Ejecutar migración completa"""
        print("🚀 Iniciando migración SQLite a MySQL...")
        print("=" * 60)
        
        try:
            # 1. Conectar bases de datos
            self.connect_databases()
            
            # 2. Crear esquema MySQL
            self.create_mysql_schema()
            
            # 3. Crear tienda principal
            main_store_id = self.create_main_store()
            
            # 4. Migrar usuarios
            self.migrate_users(main_store_id)
            
            # 5. Migrar productos a tienda
            self.migrate_products_to_store(main_store_id)
            
            # 6. Migrar ventas
            self.migrate_sales(main_store_id)
            
            # 7. Migrar movimientos de inventario
            self.migrate_inventory_movements(main_store_id)
            
            print("=" * 60)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print(f"📊 Tienda principal creada: ID {main_store_id}")
            print("📋 Log de migración:")
            for log_entry in self.migration_log:
                print(f"   - {log_entry}")
            
            return True
            
        except Exception as e:
            print(f"❌ MIGRACIÓN FALLIDA: {e}")
            return False
        
        finally:
            # Cerrar conexiones
            if self.sqlite_conn:
                self.sqlite_conn.close()
            if self.mysql_conn:
                self.mysql_conn.close()
    
    def generate_migration_report(self):
        """Generar reporte de migración"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'status': 'completed',
            'migration_log': self.migration_log,
            'sqlite_db': self.sqlite_db_path,
            'mysql_config': {
                'host': self.mysql_config['host'],
                'port': self.mysql_config['port'],
                'database': self.mysql_config['database']
            }
        }
        
        report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Reporte de migración guardado: {report_file}")

def main():
    """Función principal de migración"""
    
    # Configuración MySQL
    mysql_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'sabrositas_user'),
        'password': os.getenv('DB_PASSWORD', 'sabrositas_pass_123'),
        'database': os.getenv('DB_NAME', 'sabrositas_pos_multistore'),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    # Ruta base de datos SQLite
    sqlite_db_path = os.getenv('SQLITE_DB_PATH', 'pos_odata.db')
    
    # Verificar que existe SQLite
    if not os.path.exists(sqlite_db_path):
        print(f"❌ Base de datos SQLite no encontrada: {sqlite_db_path}")
        return False
    
    # Crear migrador y ejecutar
    migrator = SQLiteToMySQLMigrator(sqlite_db_path, mysql_config)
    success = migrator.run_migration()
    
    if success:
        migrator.generate_migration_report()
        print("\n🎉 ¡Migración completada! El sistema está listo para multi-sede.")
        print("📝 Próximos pasos:")
        print("   1. Actualizar variables de entorno para MySQL")
        print("   2. Reiniciar aplicación con docker-compose.multistore.yml")
        print("   3. Crear tiendas adicionales según necesidades")
    
    return success

if __name__ == "__main__":
    main()
