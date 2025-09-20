"""
Script para crear usuario de prueba
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def create_test_user():
    """Crear usuario de prueba"""
    print("👤 CREANDO USUARIO DE PRUEBA")
    print("=" * 40)
    
    # Datos del usuario
    user_data = {
        "username": "test_user",
        "email": "test@sabrositas.com",
        "password": "test123",
        "full_name": "Usuario de Prueba",
        "role": "admin"
    }
    
    try:
        # Intentar crear usuario
        response = requests.post(f"{BASE_URL}/api/v1/simple-users", json=user_data)
        
        if response.status_code == 201:
            print("✅ Usuario creado exitosamente")
            return True
        elif response.status_code == 400:
            print("⚠️ El usuario ya existe")
            return True
        else:
            print(f"❌ Error creando usuario: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_login():
    """Probar login con diferentes credenciales"""
    print("\n🔐 PROBANDO CREDENCIALES")
    print("=" * 40)
    
    # Credenciales a probar
    credentials = [
        {"username": "admin", "password": "admin123"},
        {"username": "test_user", "password": "test123"},
        {"username": "admin", "password": "admin"},
    ]
    
    for cred in credentials:
        print(f"\n🧪 Probando: {cred['username']} / {cred['password']}")
        
        try:
            response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=cred)
            
            if response.status_code == 200:
                print("✅ Login exitoso")
                data = response.json()
                token = data.get('access_token')
                if token:
                    print(f"🎫 Token obtenido: {token[:20]}...")
                    return cred, token
                else:
                    print("⚠️ No se recibió token")
            else:
                print(f"❌ Login fallido: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None, None

if __name__ == "__main__":
    create_test_user()
    cred, token = test_login()
    
    if token:
        print(f"\n🎉 CREDENCIALES VÁLIDAS ENCONTRADAS:")
        print(f"   Usuario: {cred['username']}")
        print(f"   Contraseña: {cred['password']}")
    else:
        print(f"\n❌ NO SE ENCONTRARON CREDENCIALES VÁLIDAS")
