"""
Tests de integración completos del sistema
"""

import asyncio
import aiohttp
import json
import sys
import time
import base64
from pathlib import Path
from datetime import datetime

# Agregar proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))


class Colors:
    """Códigos de color para terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


class TestResults:
    """Almacena resultados de tests"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name):
        self.passed += 1
        print(f"{Colors.GREEN}✓{Colors.END} {test_name}")
    
    def add_fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"{Colors.RED}✗{Colors.END} {test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}RESUMEN DE TESTS{Colors.END}")
        print("=" * 70)
        print(f"Total: {total}")
        print(f"{Colors.GREEN}Pasados: {self.passed}{Colors.END}")
        print(f"{Colors.RED}Fallidos: {self.failed}{Colors.END}")
        
        if self.errors:
            print(f"\n{Colors.RED}ERRORES:{Colors.END}")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        
        print("=" * 70)
        return self.failed == 0


async def test_health_check(base_url='http://localhost:8000'):
    """Test 1: Health check del servidor"""
    print(f"\n{Colors.BLUE}TEST 1: Health Check{Colors.END}")
    print("-" * 70)
    
    results = TestResults()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                data = await response.json()
                
                # Test: Status code 200
                if response.status == 200:
                    results.add_pass("Status code es 200")
                else:
                    results.add_fail("Status code es 200", f"Got {response.status}")
                
                # Test: Respuesta contiene 'status'
                if 'status' in data:
                    results.add_pass("Respuesta contiene 'status'")
                else:
                    results.add_fail("Respuesta contiene 'status'", "Campo faltante")
                
                # Test: Status es 'healthy'
                if data.get('status') == 'healthy':
                    results.add_pass("Status es 'healthy'")
                else:
                    results.add_fail("Status es 'healthy'", f"Got {data.get('status')}")
                
                # Test: Respuesta contiene timestamp
                if 'timestamp' in data:
                    results.add_pass("Respuesta contiene timestamp")
                else:
                    results.add_fail("Respuesta contiene timestamp", "Campo faltante")
    
    except aiohttp.ClientError as e:
        results.add_fail("Conexión al servidor", str(e))
    except Exception as e:
        results.add_fail("Test inesperado", str(e))
    
    return results


async def test_basic_scraping(base_url='http://localhost:8000'):
    """Test 2: Scraping básico sin procesamiento"""
    print(f"\n{Colors.BLUE}TEST 2: Scraping Básico{Colors.END}")
    print("-" * 70)
    
    results = TestResults()
    test_url = "https://example.com"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{base_url}/scrape?url={test_url}"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                data = await response.json()
                
                # Test: Status code 200
                if response.status == 200:
                    results.add_pass("Status code es 200")
                else:
                    results.add_fail("Status code es 200", f"Got {response.status}")
                
                # Test: Respuesta contiene scraping_data
                if 'scraping_data' in data:
                    results.add_pass("Respuesta contiene scraping_data")
                else:
                    results.add_fail("Respuesta contiene scraping_data", "Campo faltante")
                    return results
                
                scraping = data['scraping_data']
                
                # Test: Título extraído
                if scraping.get('basic', {}).get('title'):
                    results.add_pass(f"Título extraído: '{scraping['basic']['title']}'")
                else:
                    results.add_fail("Título extraído", "Título vacío")
                
                # Test: Headers extraídos
                if 'structure' in scraping and 'headers' in scraping['structure']:
                    results.add_pass("Headers extraídos")
                else:
                    results.add_fail("Headers extraídos", "Campo faltante")
                
                # Test: Links extraídos
                if 'links' in scraping:
                    results.add_pass(f"Links extraídos: {len(scraping['links'])}")
                else:
                    results.add_fail("Links extraídos", "Campo faltante")
                
                # Test: Metadata presente
                if 'metadata' in scraping:
                    results.add_pass("Metadata extraída")
                else:
                    results.add_fail("Metadata extraída", "Campo faltante")
                
                # Test: Status success
                if data.get('status') == 'success':
                    results.add_pass("Status es 'success'")
                else:
                    results.add_fail("Status es 'success'", f"Got {data.get('status')}")
    
    except aiohttp.ClientError as e:
        results.add_fail("Conexión al servidor", str(e))
    except Exception as e:
        results.add_fail("Test inesperado", str(e))
    
    return results


async def test_full_processing(base_url='http://localhost:8000'):
    """Test 3: Scraping + Procesamiento completo"""
    print(f"\n{Colors.BLUE}TEST 3: Procesamiento Completo{Colors.END}")
    print("-" * 70)
    
    results = TestResults()
    test_url = "https://example.com"
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{base_url}/scrape?url={test_url}&full=true"
            
            print(f"{Colors.YELLOW}⏳ Esperando respuesta (puede tomar hasta 60s)...{Colors.END}")
            
            start_time = time.time()
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=90)) as response:
                elapsed = time.time() - start_time
                data = await response.json()
                
                print(f"{Colors.YELLOW}⏱️  Tiempo de respuesta: {elapsed:.2f}s{Colors.END}")
                
                # Test: Status code 200
                if response.status == 200:
                    results.add_pass("Status code es 200")
                else:
                    results.add_fail("Status code es 200", f"Got {response.status}")
                
                # Test: Scraping data presente
                if 'scraping_data' in data:
                    results.add_pass("Scraping data presente")
                else:
                    results.add_fail("Scraping data presente", "Campo faltante")
                
                # Test: Processing data presente
                if 'processing_data' in data:
                    results.add_pass("Processing data presente")
                else:
                    results.add_fail("Processing data presente", "Campo faltante")
                    return results
                
                proc = data['processing_data']
                
                # Test: Screenshot generado
                if 'screenshot' in proc:
                    screenshot = proc['screenshot']
                    
                    if 'screenshot_base64' in screenshot:
                        size_kb = screenshot.get('size_bytes', 0) / 1024
                        results.add_pass(f"Screenshot generado ({size_kb:.2f} KB)")
                        
                        # Verificar que es base64 válido
                        try:
                            base64.b64decode(screenshot['screenshot_base64'][:100])
                            results.add_pass("Screenshot en base64 válido")
                        except:
                            results.add_fail("Screenshot en base64 válido", "Decodificación falló")
                    else:
                        results.add_fail("Screenshot generado", "Base64 faltante")
                else:
                    results.add_fail("Screenshot generado", "Campo faltante")
                
                # Test: Performance analizado
                if 'performance' in proc:
                    perf = proc['performance']
                    
                    if 'timing' in perf:
                        timing = perf['timing']
                        load_time = timing.get('page_load_ms', 0)
                        results.add_pass(f"Performance analizado (load: {load_time}ms)")
                    else:
                        results.add_fail("Performance timing", "Campo faltante")
                    
                    if 'resources' in perf:
                        results.add_pass("Recursos analizados")
                    else:
                        results.add_fail("Recursos analizados", "Campo faltante")
                else:
                    results.add_fail("Performance analizado", "Campo faltante")
                
                # Test: Images procesadas
                if 'images' in proc:
                    images = proc['images']
                    results.add_pass(f"Images procesadas: {images.get('total_processed', 0)}")
                else:
                    results.add_fail("Images procesadas", "Campo faltante")
                
                # Test: Tiempo de respuesta razonable
                if elapsed < 60:
                    results.add_pass(f"Tiempo de respuesta OK ({elapsed:.2f}s < 60s)")
                else:
                    results.add_fail("Tiempo de respuesta", f"{elapsed:.2f}s excede 60s")
    
    except asyncio.TimeoutError:
        results.add_fail("Timeout", "Request excedió 90 segundos")
    except aiohttp.ClientError as e:
        results.add_fail("Conexión al servidor", str(e))
    except Exception as e:
        results.add_fail("Test inesperado", str(e))
    
    return results


async def test_error_handling(base_url='http://localhost:8000'):
    """Test 4: Manejo de errores"""
    print(f"\n{Colors.BLUE}TEST 4: Manejo de Errores{Colors.END}")
    print("-" * 70)
    
    results = TestResults()
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test: URL inválida
            url = f"{base_url}/scrape?url=invalid-url"
            
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    data = await response.json()
                    
                    # Debería devolver error pero no crashear
                    if response.status >= 400 or 'error' in data or data.get('status') == 'error':
                        results.add_pass("Manejo de URL inválida")
                    else:
                        results.add_fail("Manejo de URL inválida", "No detectó error")
            
            except Exception as e:
                results.add_pass("Manejo de URL inválida (exception capturada)")
            
            # Test: URL sin parámetro
            url = f"{base_url}/scrape"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status >= 400:
                    results.add_pass("Detección de parámetro faltante")
                else:
                    results.add_fail("Detección de parámetro faltante", f"Got status {response.status}")
            
            # Test: Endpoint inexistente
            url = f"{base_url}/nonexistent"
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 404:
                    results.add_pass("404 en endpoint inexistente")
                else:
                    results.add_fail("404 en endpoint inexistente", f"Got {response.status}")
    
    except Exception as e:
        results.add_fail("Test de errores", str(e))
    
    return results


async def main():
    """Ejecutar todos los tests"""
    print("\n" + "=" * 70)
    print(f"{Colors.BOLD}🧪 SUITE DE TESTS DE INTEGRACIÓN{Colors.END}")
    print("=" * 70)
    print(f"\n{Colors.YELLOW}⚠️  Asegúrate de tener ambos servidores corriendo:{Colors.END}")
    print(f"   Terminal 1: python server_processing.py -i localhost -p 9000")
    print(f"   Terminal 2: python server_scraping.py -i localhost -p 8000")
    print()
    
    base_url = 'http://localhost:8000'
    all_results = TestResults()
    
    # Ejecutar tests
    tests = [
        ("Health Check", test_health_check(base_url)),
        ("Scraping Básico", test_basic_scraping(base_url)),
        ("Procesamiento Completo", test_full_processing(base_url)),
        ("Manejo de Errores", test_error_handling(base_url)),
    ]
    
    for test_name, test_coro in tests:
        result = await test_coro
        all_results.passed += result.passed
        all_results.failed += result.failed
        all_results.errors.extend(result.errors)
    
    # Resumen final
    success = all_results.summary()
    
    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ TODOS LOS TESTS PASARON{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ ALGUNOS TESTS FALLARON{Colors.END}")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)