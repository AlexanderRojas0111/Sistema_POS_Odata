"""
Script para encontrar credenciales válidas probando múltiples combinaciones
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_multiple_credentials():
    """Probar múltiples combinaciones de credenciales"""
    print("🔐 PROBANDO MÚLTIPLES CREDENCIALES")
    print("=" * 50)
    
    # Lista de usuarios conocidos
    users = [
        "superadmin", "techadmin", "support", "owner", 
        "globaladmin", "storeadmin1", "admin"
    ]
    
    # Lista de contraseñas comunes
    passwords = [
        "admin123", "admin", "password", "123456", 
        "superadmin", "techadmin", "support", "owner"
    ]
    
    for username in users:
        for password in passwords:
            print(f"🧪 Probando: {username} / {password}")
            
            try:
                login_data = {"username": username, "password": password}
                response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
                
                if response.status_code == 200:
                    print(f"✅ ¡CREDENCIALES VÁLIDAS ENCONTRADAS!")
                    print(f"   Usuario: {username}")
                    print(f"   Contraseña: {password}")
                    
                    # Probar un endpoint de reportes
                    token = response.json().get('access_token')
                    if token:
                        headers = {"Authorization": f"Bearer {token}"}
                        test_response = requests.get(f"{BASE_URL}/api/v1/reports/dashboard", headers=headers)
                        
                        if test_response.status_code == 200:
                            print(f"   🎯 Endpoint de reportes funciona correctamente")
                            print(f"   📊 Datos recibidos: {len(test_response.text)} bytes")
                            return username, password, token
                        else:
                            print(f"   ⚠️ Endpoint de reportes falló: {test_response.status_code}")
                    
                elif response.status_code == 401:
                    print(f"   ❌ Credenciales incorrectas")
                else:
                    print(f"   ❌ Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Error de conexión: {e}")
    
    print(f"\n❌ No se encontraron credenciales válidas")
    return None, None, None

if __name__ == "__main__":
    username, password, token = test_multiple_credentials()
    
    if token:
        print(f"\n🎉 RESULTADO EXITOSO:")
        print(f"   Usuario: {username}")
        print(f"   Contraseña: {password}")
        print(f"   Token: {token[:30]}...")
    else:
        print(f"\n💡 SUGERENCIA: Verifica que el servidor esté funcionando correctamente")
