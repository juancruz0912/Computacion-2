"""
Tests del sistema de Caché con Redis
"""
import sys
import time
from pathlib import Path

# Agregar proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.cache import RedisCache


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def test_cache():
    """Test completo del sistema de caché"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}🧪 TEST CACHÉ CON REDIS{Colors.END}")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    try:
        # Inicializar caché con TTL corto para testing
        cache = RedisCache(
            redis_host='localhost',
            redis_port=6379,
            default_ttl=5,  # 5 segundos
            key_prefix='test'
        )
        
        test_url = "https://example.com"
        test_data = {
            'title': 'Example Domain',
            'content': 'This is a test'
        }
        
        # Limpiar caché previo
        cache.clear_all()
        
        print(f"\n{Colors.YELLOW}Configuración:{Colors.END}")
        print(f"  TTL: 5 segundos")
        print(f"  URL de prueba: {test_url}")
        print()
        
        # Test 1: Cache MISS inicial
        print(f"{Colors.BOLD}Test 1: Cache MISS inicial{Colors.END}")
        
        result = cache.get(test_url)
        
        if result is None:
            print(f"  {Colors.GREEN}✓{Colors.END} Cache MISS correcto (entrada no existe)")
            passed += 1
        else:
            print(f"  {Colors.RED}✗{Colors.END} Cache HIT inesperado (debería ser MISS)")
            failed += 1
        
        # Test 2: Guardar en caché
        print(f"\n{Colors.BOLD}Test 2: Guardar en caché{Colors.END}")
        
        success = cache.set(test_url, test_data)
        
        if success:
            print(f"  {Colors.GREEN}✓{Colors.END} Datos guardados correctamente")
            passed += 1
        else:
            print(f"  {Colors.RED}✗{Colors.END} Error guardando datos")
            failed += 1
        
        # Test 3: Cache HIT
        print(f"\n{Colors.BOLD}Test 3: Cache HIT{Colors.END}")
        
        result = cache.get(test_url)
        
        if result and result.get('title') == 'Example Domain':
            print(f"  {Colors.GREEN}✓{Colors.END} Cache HIT correcto")
            print(f"    └─ Datos recuperados: {result['title']}")
            print(f"    └─ TTL restante: {result['cache']['ttl_seconds']}s")
            passed += 1
        else:
            print(f"  {Colors.RED}✗{Colors.END} Cache MISS o datos incorrectos")
            failed += 1
        
        # Test 4: Verificar existe
        print(f"\n{Colors.BOLD}Test 4: Verificar existencia{Colors.END}")
        
        exists = cache.exists(test_url)
        
        if exists:
            print(f"  {Colors.GREEN}✓{Colors.END} Entrada existe en caché")
            passed += 1
        else:
            print(f"  {Colors.RED}✗{Colors.END} Entrada no existe (debería existir)")
            failed += 1
        
        # Test 5: TTL
        print(f"\n{Colors.BOLD}Test 5: Expiración por TTL{Colors.END}")
        print(f"  {Colors.YELLOW}⏳ Esperando 6 segundos...{Colors.END}")
        
        time.sleep(6)
        
        result = cache.get(test_url)
        
        if result is None:
            print(f"  {Colors.GREEN}✓{Colors.END} Entrada expiró correctamente")
            passed += 1
        else:
            print(f"  {Colors.RED}✗{Colors.END} Entrada no expiró (debería estar vacía)")
            failed += 1
        
        # Test 6: Diferentes tipos (basic vs full)
        print(f"\n{Colors.BOLD}Test 6: Caché separado para basic y full{Colors.END}")
        
        cache.set(test_url, {'type': 'basic'}, full=False)
        cache.set(test_url, {'type': 'full'}, full=True)
        
        basic = cache.get(test_url, full=False)
        full = cache.get(test_url, full=True)
        
        if basic and full and basic['type'] == 'basic' and full['type'] == 'full':
            print(f"  {Colors.GREEN}✓{Colors.END} Cachés separados correctamente")
            print(f"    └─ Basic: {basic['type']}")
            print(f"    └─ Full: {full['type']}")
            passed += 1
        else:
            print(f"  {Colors.RED}✗{Colors.END} Cachés no están separados")
            failed += 1
        
        # Test 7: Estadísticas
        print(f"\n{Colors.BOLD}Test 7: Estadísticas{Colors.END}")
        
        stats = cache.get_stats()
        
        print(f"  Hits: {stats['hits']}")
        print(f"  Misses: {stats['misses']}")
        print(f"  Writes: {stats['writes']}")
        print(f"  Hit rate: {stats['hit_rate_percent']}%")
        
        if stats['hits'] > 0 and stats['misses'] > 0:
            print(f"  {Colors.GREEN}✓{Colors.END} Estadísticas funcionando")
            passed += 1
        else:
            print(f"  {Colors.RED}✗{Colors.END} Estadísticas incorrectas")
            failed += 1
        
        # Test 8: Limpiar caché
        print(f"\n{Colors.BOLD}Test 8: Limpiar toda la caché{Colors.END}")
        
        deleted = cache.clear_all()
        
        if deleted >= 0:
            print(f"  {Colors.GREEN}✓{Colors.END} Caché limpiado: {deleted} entradas")
            passed += 1
        else:
            print(f"  {Colors.RED}✗{Colors.END} Error limpiando caché")
            failed += 1
        
        # Limpiar y cerrar
        cache.clear_all()
        cache.close()
    
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error en tests: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        return False
    
    # Resumen
    print("\n" + "=" * 70)
    print(f"{Colors.BOLD}RESUMEN{Colors.END}")
    print(f"Total: {passed + failed}")
    print(f"{Colors.GREEN}Pasados: {passed}{Colors.END}")
    print(f"{Colors.RED}Fallidos: {failed}{Colors.END}")
    print("=" * 70)
    
    return failed == 0


if __name__ == '__main__':
    success = test_cache()
    sys.exit(0 if success else 1)