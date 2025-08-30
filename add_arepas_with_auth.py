#!/usr/bin/env python3
"""
Script para agregar todas las arepas al sistema POS con autenticación
"""

import requests
import json
import sys

# Lista de arepas con sus descripciones
arepas = [
    {"name": "LA PATRONA", "description": "Chicharrón, carne desmechada, maduro al horno y queso", "price": 10000, "category": "Arepas", "code": "ARP001"},
    {"name": "LA CAPRICHOSA", "description": "Carne desmechada, pollo, huevo y queso", "price": 10000, "category": "Arepas", "code": "ARP002"},
    {"name": "LA COMPINCHE", "description": "Carne desmechada, maduro al horno y queso", "price": 10000, "category": "Arepas", "code": "ARP003"},
    {"name": "LA COQUETA", "description": "Jamón, piña y queso", "price": 10000, "category": "Arepas", "code": "ARP004"},
    {"name": "LA CREÍDA", "description": "Pollo, salchicha y queso", "price": 10000, "category": "Arepas", "code": "ARP005"},
    {"name": "LA GOMELA", "description": "Carne, salchicha y queso", "price": 10000, "category": "Arepas", "code": "ARP006"},
    {"name": "LA CHURRA", "description": "Carne, chorizo santarrosano y queso", "price": 10000, "category": "Arepas", "code": "ARP007"},
    {"name": "LA INFIEL", "description": "Pollo, carne y queso", "price": 10000, "category": "Arepas", "code": "ARP008"},
    {"name": "LA DIFÍCIL", "description": "Carne, chorizo, jalapeño y queso", "price": 10000, "category": "Arepas", "code": "ARP009"},
    {"name": "LA CONSENTIDA", "description": "Bocadillo con queso", "price": 10000, "category": "Arepas", "code": "ARP010"},
    {"name": "LA DIVA", "description": "Carne, pollo, champiñón, salchicha y queso", "price": 10000, "category": "Arepas", "code": "ARP011"},
    {"name": "LA FÁCIL", "description": "Queso, mucho queso!", "price": 10000, "category": "Arepas", "code": "ARP012"},
    {"name": "LA SENCILLA", "description": "Jamón con queso", "price": 10000, "category": "Arepas", "code": "ARP013"},
    {"name": "LA PICANTE", "description": "Costilla BBQ, maíz tierno, tocineta, queso y ají", "price": 10000, "category": "Arepas", "code": "ARP014"},
    {"name": "LA SEXY", "description": "Pollo, champiñón y queso", "price": 10000, "category": "Arepas", "code": "ARP015"},
    {"name": "LA SOLTERA", "description": "Carne, maíz tierno y queso", "price": 10000, "category": "Arepas", "code": "ARP016"},
    {"name": "LA TÓXICA", "description": "Costilla BBQ, carne, chorizo, maíz tierno y queso", "price": 10000, "category": "Arepas", "code": "ARP017"},
    {"name": "LA SUMISA", "description": "Pollo, maíz tierno y queso", "price": 10000, "category": "Arepas", "code": "ARP018"}
]

def get_auth_token():
    """Obtener token de autenticación"""
    
    print("🔐 OBTENIENDO TOKEN DE AUTENTICACIÓN")
    print("=" * 40)
    
    try:
        url = "http://localhost:5000/api/v1/users/login"
        headers = {"Content-Type": "application/json"}
        
        login_data = {
            "email": "alexrojas8211@gmail.com",
            "password": "Alex1234."
        }
        
        response = requests.post(url, json=login_data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user_info = data.get('user', {})
            
            print("✅ Autenticación exitosa!")
            print(f"   Usuario: {user_info.get('username', 'N/A')}")
            print(f"   Rol: {user_info.get('role', 'N/A')}")
            print(f"   Token obtenido: {token[:20]}...")
            
            return token
        else:
            print(f"❌ Error en autenticación {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error obteniendo token: {str(e)}")
        return None

def add_products(token):
    """Agregar todos los productos de arepas"""
    
    if not token:
        print("❌ No hay token de autenticación disponible")
        return False
    
    base_url = "http://localhost:5000/api/v1/products/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    print("\n🥙 AGREGANDO AREPAS AL SISTEMA POS")
    print("=" * 50)
    
    successful = 0
    failed = 0
    
    for i, arepa in enumerate(arepas, 1):
        try:
            response = requests.post(base_url, json=arepa, headers=headers)
            
            if response.status_code == 201:
                product_data = response.json()
                print(f"✅ {i:2d}. {arepa['name']:<15} - ID: {product_data.get('id', 'N/A')}")
                successful += 1
            elif response.status_code == 400:
                error_msg = response.json().get('error', 'Error desconocido')
                if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                    print(f"⚠️  {i:2d}. {arepa['name']:<15} - Ya existe")
                    successful += 1  # Contar como exitoso
                else:
                    print(f"❌ {i:2d}. {arepa['name']:<15} - Error: {error_msg}")
                    failed += 1
            else:
                print(f"❌ {i:2d}. {arepa['name']:<15} - Error {response.status_code}: {response.text}")
                failed += 1
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {i:2d}. {arepa['name']:<15} - Error de conexión")
            failed += 1
        except Exception as e:
            print(f"❌ {i:2d}. {arepa['name']:<15} - Error: {str(e)}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 RESUMEN:")
    print(f"   ✅ Exitosos: {successful}")
    print(f"   ❌ Fallidos: {failed}")
    print(f"   📝 Total: {len(arepas)}")
    
    return successful > 0

def show_products(token):
    """Mostrar lista de productos"""
    
    if not token:
        return
    
    print("\n📋 PRODUCTOS EN EL SISTEMA:")
    print("=" * 35)
    
    try:
        url = "http://localhost:5000/api/v1/products/"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            products = response.json()
            items = products.get('items', [])
            total = products.get('total', 0)
            
            print(f"Total de productos: {total}")
            print("-" * 35)
            
            for product in items:
                name = product.get('name', 'N/A')
                price = product.get('price', 0)
                code = product.get('code', 'N/A')
                print(f"• {name:<18} ${price:>6,.0f} ({code})")
                
        else:
            print(f"❌ Error obteniendo productos: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Función principal"""
    
    print("🚀 AGREGANDO AREPAS AL SISTEMA POS CON AUTENTICACIÓN")
    print("=" * 60)
    
    # Paso 1: Obtener token
    token = get_auth_token()
    if not token:
        print("\n❌ No se pudo obtener token de autenticación")
        return False
    
    # Paso 2: Agregar productos
    if not add_products(token):
        print("\n❌ No se pudieron agregar los productos")
        return False
    
    # Paso 3: Mostrar productos
    show_products(token)
    
    print("\n" + "=" * 60)
    print("🎉 ¡AREPAS AGREGADAS EXITOSAMENTE!")
    print("=" * 60)
    print("✅ El menú de arepas está listo en el sistema POS")
    print("🥙 Ahora puedes procesar ventas con estos productos")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
