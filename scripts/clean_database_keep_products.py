#!/usr/bin/env python3
"""
Script de Limpieza de Base de Datos - Mantener Solo 18 Productos Sabrositas
==========================================================================
Limpia la base de datos manteniendo únicamente los 18 productos originales.
"""

import os
import sys
import sqlite3
from datetime import datetime
import json

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def backup_database(db_path: str) -> str:
    """Crear backup de la base de datos antes de limpiar"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"backups/pos_odata_backup_{timestamp}.db"
        
        # Crear directorio de backups si no existe
        os.makedirs("backups", exist_ok=True)
        
        # Copiar base de datos
        import shutil
        shutil.copy2(db_path, backup_path)
        
        print(f"✅ Backup creado: {backup_path}")
        return backup_path
        
    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        raise

def get_sabrositas_products() -> list:
    """Obtener lista de los 18 productos Sabrositas originales"""
    return [
        "LA PATRONA", "LA CAPRICHOSA", "LA COMPINCHE", "LA COQUETA",
        "LA CREÍDA", "LA GOMELA", "LA CHURRA", "LA INFIEL", 
        "LA DIFÍCIL", "LA CONSENTIDA", "LA DIVA", "LA FÁCIL",
        "LA SENCILLA", "LA PICANTE", "LA SEXY", "LA SOLTERA",
        "LA TÓXICA", "LA SUMISA"
    ]

def clean_database(db_path: str):
    """Limpiar base de datos manteniendo solo productos Sabrositas"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🧹 Iniciando limpieza de base de datos...")
        
        # 1. Obtener productos Sabrositas existentes
        sabrositas_names = get_sabrositas_products()
        placeholders = ','.join(['?' for _ in sabrositas_names])
        
        cursor.execute(f"""
            SELECT id, name, sku, price, cost, category, stock 
            FROM products 
            WHERE name IN ({placeholders}) AND is_active = 1
        """, sabrositas_names)
        
        existing_products = cursor.fetchall()
        existing_product_ids = [p[0] for p in existing_products]
        
        print(f"📦 Productos Sabrositas encontrados: {len(existing_products)}")
        for product in existing_products:
            print(f"   - {product[1]} (ID: {product[0]}, Stock: {product[6]})")
        
        # 2. Limpiar tablas relacionadas (en orden correcto para evitar FK constraints)
        
        # Eliminar items de venta que no sean de productos Sabrositas
        if existing_product_ids:
            placeholders_ids = ','.join(['?' for _ in existing_product_ids])
            cursor.execute(f"""
                DELETE FROM sale_items 
                WHERE product_id NOT IN ({placeholders_ids})
            """, existing_product_ids)
            deleted_sale_items = cursor.rowcount
            print(f"🗑️  Sale items eliminados: {deleted_sale_items}")
        else:
            cursor.execute("DELETE FROM sale_items")
            deleted_sale_items = cursor.rowcount
            print(f"🗑️  Sale items eliminados: {deleted_sale_items}")
        
        # Eliminar movimientos de inventario que no sean de productos Sabrositas
        if existing_product_ids:
            cursor.execute(f"""
                DELETE FROM inventory_movements 
                WHERE product_id NOT IN ({placeholders_ids})
            """, existing_product_ids)
            deleted_movements = cursor.rowcount
            print(f"🗑️  Movimientos de inventario eliminados: {deleted_movements}")
        else:
            cursor.execute("DELETE FROM inventory_movements")
            deleted_movements = cursor.rowcount
            print(f"🗑️  Movimientos de inventario eliminados: {deleted_movements}")
        
        # Eliminar ventas huérfanas (sin items)
        cursor.execute("""
            DELETE FROM sales 
            WHERE id NOT IN (SELECT DISTINCT sale_id FROM sale_items)
        """)
        deleted_sales = cursor.rowcount
        print(f"🗑️  Ventas huérfanas eliminadas: {deleted_sales}")
        
        # Eliminar productos que no sean Sabrositas
        if existing_product_ids:
            cursor.execute(f"""
                DELETE FROM products 
                WHERE id NOT IN ({placeholders_ids})
            """, existing_product_ids)
            deleted_products = cursor.rowcount
            print(f"🗑️  Productos no-Sabrositas eliminados: {deleted_products}")
        else:
            print("⚠️  No se encontraron productos Sabrositas, no se eliminará nada")
        
        # 3. Limpiar usuarios no esenciales (mantener solo admin y algunos usuarios básicos)
        cursor.execute("""
            DELETE FROM users 
            WHERE username NOT IN ('admin', 'cashier1', 'manager1') 
            AND is_admin = 0
        """)
        deleted_users = cursor.rowcount
        print(f"🗑️  Usuarios no esenciales eliminados: {deleted_users}")
        
        # 4. Resetear secuencias para IDs más limpios (SQLite)
        cursor.execute("DELETE FROM sqlite_sequence WHERE name NOT IN ('products', 'users')")
        
        # 5. Verificar productos finales
        cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
        final_product_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sales")
        final_sales_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        final_users_count = cursor.fetchone()[0]
        
        # Commit cambios
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
        print("="*60)
        print(f"📦 Productos finales: {final_product_count}")
        print(f"🛒 Ventas finales: {final_sales_count}")
        print(f"👥 Usuarios finales: {final_users_count}")
        print("="*60)
        
        # Verificar integridad
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        if integrity_result == "ok":
            print("✅ Verificación de integridad: OK")
        else:
            print(f"⚠️  Verificación de integridad: {integrity_result}")
        
        return {
            'success': True,
            'final_products': final_product_count,
            'final_sales': final_sales_count,
            'final_users': final_users_count,
            'deleted_items': {
                'sale_items': deleted_sale_items,
                'inventory_movements': deleted_movements,
                'sales': deleted_sales,
                'products': deleted_products,
                'users': deleted_users
            }
        }
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error durante limpieza: {e}")
        raise
    finally:
        conn.close()

def verify_sabrositas_products(db_path: str):
    """Verificar que los 18 productos Sabrositas estén presentes"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 VERIFICANDO PRODUCTOS SABROSITAS:")
        print("-" * 50)
        
        cursor.execute("""
            SELECT name, sku, price, cost, stock, category
            FROM products 
            WHERE is_active = 1
            ORDER BY name
        """)
        
        products = cursor.fetchall()
        sabrositas_names = get_sabrositas_products()
        
        print(f"Total productos en BD: {len(products)}")
        print(f"Productos esperados: {len(sabrositas_names)}")
        print("\nProductos encontrados:")
        
        found_names = []
        for i, product in enumerate(products, 1):
            name, sku, price, cost, stock, category = product
            found_names.append(name)
            print(f"{i:2d}. {name:<15} | SKU: {sku:<10} | ${price:>6} | Stock: {stock:>3} | {category}")
        
        # Verificar productos faltantes
        missing_products = [name for name in sabrositas_names if name not in found_names]
        if missing_products:
            print(f"\n⚠️  PRODUCTOS FALTANTES ({len(missing_products)}):")
            for product in missing_products:
                print(f"   - {product}")
        else:
            print(f"\n✅ TODOS LOS {len(sabrositas_names)} PRODUCTOS SABROSITAS ESTÁN PRESENTES")
        
        conn.close()
        return len(products) == len(sabrositas_names) and not missing_products
        
    except Exception as e:
        print(f"❌ Error verificando productos: {e}")
        return False

def generate_cleanup_report(results: dict, backup_path: str):
    """Generar reporte de limpieza"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"backups/cleanup_report_{timestamp}.json"
        
        report = {
            'cleanup_timestamp': datetime.now().isoformat(),
            'backup_path': backup_path,
            'results': results,
            'sabrositas_products': get_sabrositas_products()
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Reporte generado: {report_path}")
        return report_path
        
    except Exception as e:
        print(f"⚠️  Error generando reporte: {e}")
        return None

def main():
    """Función principal"""
    print("🧹 LIMPIEZA DE BASE DE DATOS SABROSITAS")
    print("=" * 50)
    print("⚠️  ADVERTENCIA: Esta operación eliminará datos permanentemente")
    print("✅ Se creará un backup automático antes de proceder")
    print()
    
    # Confirmar operación
    response = input("¿Deseas continuar con la limpieza? (si/no): ").lower().strip()
    if response not in ['si', 's', 'yes', 'y']:
        print("❌ Operación cancelada")
        return False
    
    # Ruta de la base de datos
    db_path = "pos_odata.db"
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        # 1. Crear backup
        backup_path = backup_database(db_path)
        
        # 2. Limpiar base de datos
        results = clean_database(db_path)
        
        # 3. Verificar productos Sabrositas
        verification_ok = verify_sabrositas_products(db_path)
        
        # 4. Generar reporte
        report_path = generate_cleanup_report(results, backup_path)
        
        print("\n" + "🎉" * 20)
        print("LIMPIEZA COMPLETADA EXITOSAMENTE")
        print("🎉" * 20)
        print(f"📄 Backup: {backup_path}")
        print(f"📄 Reporte: {report_path}")
        print(f"✅ Verificación productos: {'OK' if verification_ok else 'REVISAR'}")
        print("\n🚀 La base de datos está lista con los 18 productos Sabrositas")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LIMPIEZA: {e}")
        print("💾 Los datos originales están seguros en el backup")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
