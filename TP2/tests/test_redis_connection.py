"""
Test básico de conexión a Redis
"""
import redis
import sys

def test_redis_connection():
    """Verifica que Redis esté corriendo y accesible"""
    try:
        # Conectar a Redis
        r = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Test PING
        response = r.ping()
        
        if response:
            print("✅ Redis conectado correctamente")
            print(f"   Host: localhost:6379")
            
            # Test básico de SET/GET
            r.set('test_key', 'test_value')
            value = r.get('test_key')
            
            if value == 'test_value':
                print("✅ Operaciones SET/GET funcionando")
            
            # Limpiar
            r.delete('test_key')
            
            # Info del servidor
            info = r.info('server')
            print(f"   Redis version: {info.get('redis_version')}")
            print(f"   Uptime: {info.get('uptime_in_seconds')} segundos")
            
            return True
        
    except redis.ConnectionError:
        print("❌ Error: No se pudo conectar a Redis")
        print("   Asegúrate de que Redis esté corriendo:")
        print("   sudo systemctl start redis-server")
        return False
    
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == '__main__':
    success = test_redis_connection()
    sys.exit(0 if success else 1)