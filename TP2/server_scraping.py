import asyncio
import aiohttp
from aiohttp import web
import argparse
from datetime import datetime
import logging

# Importar módulos de scraping
from scraper import HtmlParser, MetadataExtractor, AsyncHttpClient
from common.async_client import ProcessingClient

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScrapingServer:
    """Servidor HTTP asíncrono para scraping web"""
    
    def __init__(self, host, port, workers=4, processing_host='localhost', processing_port=9000):
        self.host = host
        self.port = port
        self.workers = workers
        self.app = web.Application()
        
        # Cliente HTTP para scraping
        self.http_client = AsyncHttpClient(timeout=30)
        
        # Cliente para comunicarse con el Servidor B
        self.processing_client = ProcessingClient(processing_host, processing_port)
        
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
        Query params: 
            - url (requerido): URL a scrapear
            - full (opcional): Si es 'true', solicita procesamiento completo al Servidor B
        """
        try:
            # Obtener parámetros
            url = request.query.get('url')
            full_processing = request.query.get('full', 'false').lower() == 'true'
            
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
            
            logger.info(f"🔍 Scraping URL: {url} (full={full_processing})")
            
            # Realizar el scraping completo
            scraping_data = await self.scrape_url(url)
            
            # Construir respuesta base
            response = {
                'url': url,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'scraping_data': scraping_data,
                'status': 'success'
            }
            
            # Si se solicita procesamiento completo, comunicarse con el Servidor B
            if full_processing:
                logger.info(f"🔄 Solicitando procesamiento completo para {url}")
                
                try:
                    # Solicitar procesamiento al Servidor B
                    processing_result = await self.processing_client.request_all(url)
                    
                    # Agregar los resultados del procesamiento
                    if processing_result.get('status') == 'success':
                        response['processing_data'] = processing_result.get('result', {})
                        logger.info("✅ Procesamiento completado exitosamente")
                    else:
                        response['processing_error'] = processing_result.get('error_message', 'Unknown error')
                        logger.warning(f"⚠️  Error en procesamiento: {response['processing_error']}")
                
                except Exception as e:
                    logger.error(f"❌ Error comunicándose con servidor de procesamiento: {e}")
                    response['processing_error'] = f"Processing server unavailable: {str(e)}"
            
            return web.json_response(response)
        
        except asyncio.TimeoutError:
            logger.error(f"⏱️  Timeout scraping {url}")
            return web.json_response({
                'status': 'error',
                'message': 'Request timeout (30 seconds)'
            }, status=408)
        
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {str(e)}")
            return web.json_response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    async def scrape_url(self, url):
        """
        Realizar el scraping completo de una URL
        
        Args:
            url: URL a scrapear
            
        Returns:
            dict con todos los datos extraídos
        """
        # Descargar la página
        status, html, headers = await self.http_client.fetch(url)
        
        if status != 200:
            raise Exception(f"HTTP {status}")
        
        # Parsear HTML
        parser = HtmlParser(html, url)
        metadata_extractor = MetadataExtractor(html)
        
        # Extraer toda la información
        scraping_data = {
            'basic': {
                'title': parser.extract_title(),
                'text_preview': parser.extract_text_content(max_length=200),
                'word_count': len(html.split())
            },
            'structure': {
                'headers': parser.extract_headers(),
                'headers_content': parser.extract_headers_content(),
                'elements_count': parser.count_elements()
            },
            'links': parser.extract_links(limit=30),
            'images': parser.extract_images(limit=10),
            'metadata': metadata_extractor.extract_all(),
            'response': {
                'status_code': status,
                'content_type': headers.get('Content-Type', ''),
                'content_length': headers.get('Content-Length', ''),
                'server': headers.get('Server', '')
            }
        }
        
        return scraping_data
    
    async def start(self):
        """Iniciar el servidor"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"🚀 Servidor de Scraping iniciado en {self.host}:{self.port}")
        logger.info(f"📊 Workers configurados: {self.workers}")
        logger.info(f"🔗 Servidor de procesamiento: {self.processing_client.host}:{self.processing_client.port}")
        logger.info(f"💡 Prueba con: http://{self.host}:{self.port}/scrape?url=https://example.com&full=true")
        
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("🛑 Deteniendo servidor...")
        finally:
            await runner.cleanup()


def parse_arguments():
    """Parsear argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Servidor de Scraping Web Asíncrono',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-i', '--ip', required=True, help='Dirección de escucha')
    parser.add_argument('-p', '--port', type=int, required=True, help='Puerto de escucha')
    parser.add_argument('-w', '--workers', type=int, default=4, help='Número de workers')
    parser.add_argument('--processing-host', default='localhost', help='Host del servidor de procesamiento')
    parser.add_argument('--processing-port', type=int, default=9000, help='Puerto del servidor de procesamiento')
    
    return parser.parse_args()


async def main():
    args = parse_arguments()
    server = ScrapingServer(
        host=args.ip,
        port=args.port,
        workers=args.workers,
        processing_host=args.processing_host,
        processing_port=args.processing_port
    )
    await server.start()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")