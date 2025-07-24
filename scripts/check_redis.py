import redis
import sys
from config import Config

def check_redis_connection():
    """Verifica la conexión con Redis"""
    try:
        # Intentar conectar a Redis
        redis_client = redis.from_url(Config.REDIS_URL)
        
        # Probar operaciones básicas
        redis_client.set('test_key', 'test_value')
        value = redis_client.get('test_key')
        
        if value.decode('utf-8') == 'test_value':
            print("✅ Conexión a Redis exitosa")
            print(f"URL de Redis: {Config.REDIS_URL}")
            
            # Limpiar la clave de prueba
            redis_client.delete('test_key')
            return True
    except redis.ConnectionError as e:
        print("❌ Error al conectar con Redis:")
        print(f"Error: {str(e)}")
        print("\nPosibles soluciones:")
        print("1. Asegúrate de que Redis está instalado y ejecutándose")
        print("2. Verifica que la URL de Redis es correcta en la configuración")
        print("3. Para Windows, puedes descargar Redis desde: https://github.com/microsoftarchive/redis/releases")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

if __name__ == '__main__':
    success = check_redis_connection()
    sys.exit(0 if success else 1) 