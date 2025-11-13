"""
Tests del Rate Limiter con Redis
"""
import sys
import time
from pathlib import Path

# Agregar proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.rate_limiter import RateLimiter


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def test_rate_limiter():
    """Test completo del Rate Limiter"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}🧪 TEST RATE LIMITER{Colors.END}")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    try:
        # Inicializar con límite bajo para testing
        limiter = RateLimiter(
            redis_host='localhost',
            redis_port=6379,
            max_requests=3,  # Solo 3 requests
            window_seconds=10  # En 10 segundos
        )
        
        test_url = "https://example.com/test"
        
        # Limpiar estado previo
        limiter.reset_domain(test_url)
        
        print(f"\n{Colors.YELLOW}Configuración:{Colors.END}")
        print(f"  Límite: 3 requests / 10 segundos")
        print(f"  URL de prueba: {test_url}")
        print()
        
        # Test 1: Primeras 3 requests deben pasar
        print(f"{Colors.BOLD}Test 1: Requests dentro del límite{Colors.END}")
        
        for i in range(3):
            allowed, info = limiter.check_rate_limit(test_url)
            
            if allowed:
                print(f"  {Colors.GREEN}✓{Colors.END} Request {i+1}: Permitido "
                      f"(remaining: {info['remaining']})")
                passed += 1
            else:
                print(f"  {Colors.RED}✗{Colors.END} Request {i+1}: Bloqueado (debería estar permitido)")
                failed += 1
        
        # Test 2: Cuarta request debe fallar
        print(f"\n{Colors.BOLD}Test 2: Request que excede el límite{Colors.END}")
        
        allowed, info = limiter.check_rate_limit(test_url)
        
        if not allowed:
            print(f"  {Colors.GREEN}✓{Colors.END} Request 4: Correctamente bloqueado")
            print(f"    └─ {info['requests_in_window']}/{info['max_requests']} requests en ventana")
            passed += 1
        else:
            print(f"  {Colors.RED}✗{Colors.END} Request 4: Permitido (debería estar bloqueado)")
            failed += 1
        
        # Test 3: Verificar estadísticas
        print(f"\n{Colors.BOLD}Test 3: Estadísticas{Colors.END}")
        
        stats = limiter.get_stats(test_url)
        
        print(f"  Domain: {stats['domain']}")
        print(f"  Requests: {stats['request_count']}/{stats['max_requests']}")
        print(f"  Allowed: {stats['allowed']}")
        print(f"  Remaining: {stats['remaining']}")
        
        if stats['request_count'] == 3 and not stats['allowed']:
            print(f"  {Colors.GREEN}✓{Colors.END} Estadísticas correctas")
            passed += 1
        else:
            print(f"  {Colors.RED}✗{Colors.END} Estadísticas incorrectas")
            failed += 1
        
        # Test 4: Esperar y verificar ventana deslizante
        print(f"\n{Colors.BOLD}Test 4: Ventana deslizante{Colors.END}")
        print(f"  {Colors.YELLOW}⏳ Esperando 11 segundos...{Colors.END}")
        
        time.sleep(11)
        
        allowed, info = limiter.check_rate_limit(test_url)
        
        if allowed:
            print(f"  {Colors.GREEN}✓{Colors.END} Request después de ventana: Permitido")
            print(f"    └─ Ventana reseteada correctamente")
            passed += 1
        else:
            print(f"  {Colors.RED}✗{Colors.END} Request después de ventana: Bloqueado")
            failed += 1
        
        # Test 5: Dominios diferentes son independientes
        print(f"\n{Colors.BOLD}Test 5: Dominios independientes{Colors.END}")
        
        other_url = "https://other-domain.com/test"
        limiter.reset_domain(other_url)
        
        allowed, info = limiter.check_rate_limit(other_url)
        
        if allowed:
            print(f"  {Colors.GREEN}✓{Colors.END} Otro dominio: Permitido (límite independiente)")
            passed += 1
        else:
            print(f"  {Colors.RED}✗{Colors.END} Otro dominio: Bloqueado (no debería)")
            failed += 1
        
        # Limpiar
        limiter.reset_domain(test_url)
        limiter.reset_domain(other_url)
        limiter.close()
    
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error en tests: {e}{Colors.END}")
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
    success = test_rate_limiter()
    sys.exit(0 if success else 1)