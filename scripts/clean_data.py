#!/usr/bin/env python3
"""
Script de Limpieza de Datos - O'Data v2.0.0
============================================

Script consolidado para limpiar diferentes tipos de datos del sistema

Autor: Sistema POS Odata
Versión: 2.0.0
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app import db
from app.models.customer import Customer
from app.models.product import Product
from app.models.sale import Sale
from app.models.inventory import Inventory

def clean_customers():
    """Limpiar todos los clientes"""
    try:
        confirm = input("¿Seguro que deseas eliminar TODOS los clientes? (s/n): ")
        if confirm.lower() == 's':
            deleted = Customer.query.delete()
            db.session.commit()
            print(f"✅ {deleted} clientes eliminados.")
            return True
        else:
            print("❌ Operación cancelada.")
            return False
    except Exception as e:
        print(f"❌ Error eliminando clientes: {e}")
        return False

def clean_products():
    """Limpiar todos los productos"""
    try:
        confirm = input("¿Seguro que deseas eliminar TODOS los productos? (s/n): ")
        if confirm.lower() == 's':
            deleted = Product.query.delete()
            db.session.commit()
            print(f"✅ {deleted} productos eliminados.")
            return True
        else:
            print("❌ Operación cancelada.")
            return False
    except Exception as e:
        print(f"❌ Error eliminando productos: {e}")
        return False

def clean_sales():
    """Limpiar todas las ventas"""
    try:
        confirm = input("¿Seguro que deseas eliminar TODAS las ventas? (s/n): ")
        if confirm.lower() == 's':
            deleted = Sale.query.delete()
            db.session.commit()
            print(f"✅ {deleted} ventas eliminadas.")
            return True
        else:
            print("❌ Operación cancelada.")
            return False
    except Exception as e:
        print(f"❌ Error eliminando ventas: {e}")
        return False

def clean_inventory():
    """Limpiar todo el inventario"""
    try:
        confirm = input("¿Seguro que deseas eliminar TODO el inventario? (s/n): ")
        if confirm.lower() == 's':
            deleted = Inventory.query.delete()
            db.session.commit()
            print(f"✅ {deleted} registros de inventario eliminados.")
            return True
        else:
            print("❌ Operación cancelada.")
            return False
    except Exception as e:
        print(f"❌ Error eliminando inventario: {e}")
        return False

def clean_all_data():
    """Limpiar todos los datos"""
    try:
        confirm = input("⚠️  ¿Seguro que deseas eliminar TODOS los datos? (s/n): ")
        if confirm.lower() == 's':
            print("🗑️  Eliminando todos los datos...")
            
            # Eliminar en orden para evitar problemas de integridad referencial
            Inventory.query.delete()
            Sale.query.delete()
            Product.query.delete()
            Customer.query.delete()
            
            db.session.commit()
            print("✅ Todos los datos eliminados.")
            return True
        else:
            print("❌ Operación cancelada.")
            return False
    except Exception as e:
        print(f"❌ Error eliminando datos: {e}")
        return False

def main():
    """Función principal"""
    print("🧹 SCRIPT DE LIMPIEZA DE DATOS - O'DATA v2.0.0")
    print("=" * 50)
    
    try:
        # Crear aplicación
        app = create_app('development')
        
        with app.app_context():
            print("\n📋 OPCIONES DISPONIBLES:")
            print("1. Limpiar clientes")
            print("2. Limpiar productos")
            print("3. Limpiar ventas")
            print("4. Limpiar inventario")
            print("5. Limpiar TODOS los datos")
            print("6. Salir")
            
            while True:
                try:
                    option = input("\n🔢 Selecciona una opción (1-6): ").strip()
                    
                    if option == '1':
                        clean_customers()
                    elif option == '2':
                        clean_products()
                    elif option == '3':
                        clean_sales()
                    elif option == '4':
                        clean_inventory()
                    elif option == '5':
                        clean_all_data()
                    elif option == '6':
                        print("👋 ¡Hasta luego!")
                        break
                    else:
                        print("❌ Opción no válida. Selecciona 1-6.")
                        
                except KeyboardInterrupt:
                    print("\n\n👋 Operación cancelada por el usuario.")
                    break
                except Exception as e:
                    print(f"❌ Error inesperado: {e}")
                    
    except Exception as e:
        print(f"❌ Error inicializando aplicación: {e}")
        print("💡 Asegúrate de que el entorno esté configurado correctamente.")

if __name__ == "__main__":
    main()
