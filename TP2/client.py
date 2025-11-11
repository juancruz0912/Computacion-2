import asyncio
import aiohttp
import json
import argparse
from urllib.parse import urlencode


async def test_scrape(server_url, target_url):
    """
    Probar el endpoint de scraping
    
    Args:
        server_url: URL del servidor (ej: http://localhost:8000)
        target_url: URL a scrapear
    """
    endpoint = f"{server_url}/scrape?url={target_url}"
    
    print(f"📡 Enviando request a: {endpoint}")
    print(f"🎯 Target URL: {target_url}\n")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(endpoint) as response:
                print(f"📊 Status: {response.status}")
                print(f"📋 Headers: {dict(response.headers)}\n")
                
                data = await response.json()
                
                print("📦 Respuesta:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                return data
        
        except aiohttp.ClientError as e:
            print(f"❌ Error de conexión: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")


async def test_health(server_url):
    """Probar el endpoint de health check"""
    endpoint = f"{server_url}/health"
    
    print(f"💓 Health check: {endpoint}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(endpoint) as response:
                data = await response.json()
                print(f"✅ Server is {data['status']}")
                return data
        except Exception as e:
            print(f"❌ Server is down: {e}")


async def main():
    """Función principal del cliente"""
    parser = argparse.ArgumentParser(description='Cliente de prueba para el servidor de scraping')
    
    parser.add_argument(
        '-s', '--server',
        default='http://localhost:8000',
        help='URL del servidor (default: http://localhost:8000)'
    )
    
    parser.add_argument(
        '-u', '--url',
        help='URL a scrapear'
    )
    
    parser.add_argument(
        '--health',
        action='store_true',
        help='Realizar solo health check'
    )
    
    args = parser.parse_args()
    
    if args.health:
        await test_health(args.server)
    elif args.url:
        await test_scrape(args.server, args.url)
    else:
        print("❌ Debes especificar --url o --health")
        print("\nEjemplos de uso:")
        print(f"  python client.py --health")
        print(f"  python client.py --url https://example.com")
        print(f"  python client.py -s http://localhost:8000 -u https://python.org")


if __name__ == '__main__':
    asyncio.run(main())