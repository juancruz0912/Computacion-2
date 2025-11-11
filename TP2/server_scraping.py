import asyncio
import aiohttp
from aiohttp import web
from bs4 import BeautifulSoup
import argparse
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScrapingServer:
    """Servidor HTTP asíncrono para scraping web"""
    
    def __init__(self, host, port, workers=4):
        self.host = host
        self.port = port
        self.workers = workers
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Configurar las rutas del servidor"""
        self.app.router.add_get('/scrape', self.handle_scrape)
        self.app.router.add_get('/health', self.handle_health)
    
    async def handle_health(self, request):
        """Endpoint de health check"""
        return web.json_response({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
    
    async def handle_scrape(self, request):
        """
        Endpoint principal de scraping
        Query params: url (requerido)
        """
        try:
            # Obtener URL del query parameter
            url = request.query.get('url')
            
            if not url:
                return web.json_response({
                    'status': 'error',
                    'message': 'URL parameter is required'
                }, status=400)
            
            # Validar que la URL comience con http:// o https://
            if not url.startswith(('http://', 'https://')):
                return web.json_response({
                    'status': 'error',
                    'message': 'URL must start with http:// or https://'
                }, status=400)
            
            logger.info(f"Scraping URL: {url}")
            
            # Realizar el scraping
            scraping_data = await self.scrape_url(url)
            
            # Construir respuesta
            response = {
                'url': url,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'scraping_data': scraping_data,
                'status': 'success'
            }
            
            return web.json_response(response)
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout scraping {url}")
            return web.json_response({
                'status': 'error',
                'message': 'Request timeout (30 seconds)'
            }, status=408)
        
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return web.json_response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    async def scrape_url(self, url):
        """
        Realizar el scraping de una URL de forma asíncrona
        
        Args:
            url: URL a scrapear
            
        Returns:
            dict con los datos extraídos
        """
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                
                # Verificar que la respuesta sea exitosa
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}: {response.reason}")
                
                # Leer el contenido HTML
                html = await response.text()
                
                # Parsear con BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extraer información básica
                scraping_data = {
                    'title': self.extract_title(soup),
                    'links': self.extract_links(soup, url),
                    'images_count': len(soup.find_all('img')),
                }
                
                return scraping_data
    
    def extract_title(self, soup):
        """Extraer el título de la página"""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else 'No title found'
    
    def extract_links(self, soup, base_url):
        """
        Extraer todos los enlaces de la página
        
        Args:
            soup: BeautifulSoup object
            base_url: URL base para resolver enlaces relativos
            
        Returns:
            list de URLs absolutas
        """
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Convertir enlaces relativos a absolutos
            if href.startswith('http'):
                links.append(href)
            elif href.startswith('/'):
                # Extraer el dominio base
                from urllib.parse import urljoin
                absolute_url = urljoin(base_url, href)
                links.append(absolute_url)
        
        # Eliminar duplicados manteniendo el orden
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        return unique_links[:50]  # Limitar a 50 links para evitar respuestas muy grandes
    
    async def start(self):
        """Iniciar el servidor"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"🚀 Servidor de Scraping iniciado en {self.host}:{self.port}")
        logger.info(f"📊 Workers configurados: {self.workers}")
        logger.info(f"🔗 Prueba con: http://{self.host}:{self.port}/scrape?url=https://example.com")
        
        # Mantener el servidor corriendo
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Deteniendo servidor...")
        finally:
            await runner.cleanup()


def parse_arguments():
    """Parsear argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Servidor de Scraping Web Asíncrono',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--ip',
        required=True,
        help='Dirección de escucha (soporta IPv4/IPv6)'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        required=True,
        help='Puerto de escucha'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=4,
        help='Número de workers (default: 4)'
    )
    
    return parser.parse_args()


async def main():
    """Función principal"""
    args = parse_arguments()
    
    server = ScrapingServer(
        host=args.ip,
        port=args.port,
        workers=args.workers
    )
    
    await server.start()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")