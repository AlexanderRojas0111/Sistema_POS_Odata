#!/usr/bin/env python3
"""
Script para corregir la base de datos y agregar columnas de pagos múltiples
=======================================================================
"""

import sqlite3
import os
from datetime import datetime

def fix_database():
    """Corregir la base de datos agregando columnas faltantes"""
    
    db_path = "instance/pos_odata.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔧 CORRIGIENDO BASE DE DATOS...")
        print("=" * 50)
        
        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(sales)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Agregar columnas faltantes a la tabla sales
        if 'is_multi_payment' not in columns:
            print("➕ Agregando columna 'is_multi_payment' a tabla 'sales'...")
            cursor.execute("ALTER TABLE sales ADD COLUMN is_multi_payment BOOLEAN DEFAULT 0")
        
        if 'multi_payment_id' not in columns:
            print("➕ Agregando columna 'multi_payment_id' a tabla 'sales'...")
            cursor.execute("ALTER TABLE sales ADD COLUMN multi_payment_id INTEGER")
        
        # Crear tabla multi_payments si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS multi_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                sale_id INTEGER UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                total_amount DECIMAL(15,2) NOT NULL,
                paid_amount DECIMAL(15,2) DEFAULT 0.0,
                change_amount DECIMAL(15,2) DEFAULT 0.0,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sale_id) REFERENCES sales (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        print("✅ Tabla 'multi_payments' creada/verificada")
        
        # Crear tabla payment_details si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                multi_payment_id INTEGER NOT NULL,
                payment_method TEXT NOT NULL,
                amount DECIMAL(15,2) NOT NULL,
                reference TEXT,
                bank_name TEXT,
                card_last_four TEXT,
                phone_number TEXT,
                qr_code TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (multi_payment_id) REFERENCES multi_payments (id)
            )
        """)
        print("✅ Tabla 'payment_details' creada/verificada")
        
        # Crear índices para optimización
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_is_multi_payment ON sales(is_multi_payment)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_multi_payment_id ON sales(multi_payment_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_multi_payments_sale_id ON multi_payments(sale_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_multi_payments_user_id ON multi_payments(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_details_multi_payment_id ON payment_details(multi_payment_id)")
        
        print("✅ Índices creados/verificados")
        
        # Commit cambios
        conn.commit()
        print("✅ Cambios guardados en base de datos")
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"\n📋 Tablas en base de datos: {', '.join(tables)}")
        
        # Verificar columnas de sales
        cursor.execute("PRAGMA table_info(sales)")
        sales_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Columnas en tabla 'sales': {', '.join(sales_columns)}")
        
        conn.close()
        
        print("\n🎉 BASE DE DATOS CORREGIDA EXITOSAMENTE")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo base de datos: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 CORRECTOR DE BASE DE DATOS - PAGOS MÚLTIPLES")
    print("=" * 60)
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = fix_database()
    
    if success:
        print("\n✅ Sistema listo para despliegue")
    else:
        print("\n❌ Error en corrección de base de datos")
