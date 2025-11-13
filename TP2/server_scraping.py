"""
Servidor A: Scraping Asíncrono con Rate Limiting y Caché
"""
import asyncio
import aiohttp
from aiohttp import web
import argparse
import logging
from datetime import datetime

from scraper.html_parser import HtmlParser
from common.protocol import Protocol, MessageType, TaskType

from common.rate_limiter import init_rate_limiter, get_rate_limiter
from common.cache import init_cache, get_cache

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScrapingServer:
    """Servidor HTTP asíncrono para scraping de páginas web"""
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8000,
        processing_host: str = 'localhost',
        processing_port: int = 9000,
        redis_host: str = 'localhost',
        redis_port: int = 6379,
        enable_cache: bool = True,
        enable_rate_limit: bool = True,
        max_requests_per_minute: int = 10,
        cache_ttl: int = 3600
    ):
        self.host = host
        self.port = port
        self.processing_host = processing_host
        self.processing_port = processing_port
        
        # Configuración de Redis
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.enable_cache = enable_cache
        self.enable_rate_limit = enable_rate_limit
        self.max_requests_per_minute = max_requests_per_minute
        self.cache_ttl = cache_ttl
        
        self.html_parser = HtmlParser()
        self.protocol = Protocol()
        
        # Rate Limiter y Caché
        self.rate_limiter = None
        self.cache = None
    
    async def _init_redis_services(self):
        """Inicializa servicios de Redis (Rate Limiter y Caché)"""
        try:
            # Inicializar Rate Limiter
            if self.enable_rate_limit:
                self.rate_limiter = init_rate_limiter(
                    redis_host=self.redis_host,
                    redis_port=self.redis_port,
                    max_requests=self.max_requests_per_minute,
                    window_seconds=60
                )
                logger.info(
                    f"✅ Rate Limiter habilitado: "
                    f"{self.max_requests_per_minute} req/min por dominio"
                )
            else:
                logger.info("⚠️  Rate Limiter deshabilitado")
            
            # Inicializar Caché
            if self.enable_cache:
                self.cache = init_cache(
                    redis_host=self.redis_host,
                    redis_port=self.redis_port,
                    default_ttl=self.cache_ttl
                )
                logger.info(
                    f"✅ Caché habilitado: TTL={self.cache_ttl}s"
                )
            else:
                logger.info("⚠️  Caché deshabilitado")
        
        except Exception as e:
            logger.error(f"❌ Error inicializando servicios de Redis: {e}")
            logger.warning("⚠️  Servidor continuará sin Rate Limiting ni Caché")
            self.enable_rate_limit = False
            self.enable_cache = False
    
    async def health_handler(self, request):
        """Endpoint de health check"""
        response = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'services': {
                'rate_limiter': 'enabled' if self.enable_rate_limit else 'disabled',
                'cache': 'enabled' if self.enable_cache else 'disabled'
            }
        }
        
        # Agregar estadísticas de caché si está habilitado
        if self.enable_cache and self.cache:
            try:
                cache_stats = self.cache.get_stats()
                response['cache_stats'] = cache_stats
            except:
                pass
        
        return web.json_response(response)
    
    async def scrape_handler(self, request):
        """Endpoint principal de scraping"""
        try:
            # Obtener parámetros
            url = request.query.get('url')
            full = request.query.get('full', 'false').lower() == 'true'
            
            if not url:
                return web.json_response(
                    {'error': 'URL parameter is required'},
                    status=400
                )
            
            logger.info(f"📥 Request recibido: {url} (full={full})")
            
            # VERIFICAR RATE LIMIT
            if self.enable_rate_limit and self.rate_limiter:
                allowed, rate_info = self.rate_limiter.check_rate_limit(url)
                
                if not allowed:
                    logger.warning(
                        f"⚠️  Rate limit excedido para {rate_info['domain']}: "
                        f"{rate_info['requests_in_window']}/{rate_info['max_requests']}"
                    )
                    
                    return web.json_response(
                        {
                            'error': 'Rate limit exceeded',
                            'message': f"Too many requests to {rate_info['domain']}",
                            'rate_limit': {
                                'limit': rate_info['max_requests'],
                                'window_seconds': rate_info['window_seconds'],
                                'retry_after': rate_info['window_seconds']
                            }
                        },
                        status=429,
                        headers={
                            'Retry-After': str(rate_info['window_seconds']),
                            'X-RateLimit-Limit': str(rate_info['max_requests']),
                            'X-RateLimit-Remaining': str(rate_info['remaining'])
                        }
                    )
            
            # VERIFICAR CACHÉ
            if self.enable_cache and self.cache:
                cached_data = self.cache.get(url, full)
                
                if cached_data:
                    logger.info(
                        f"✅ Respuesta desde caché: {url} "
                        f"(TTL: {cached_data['cache']['ttl_seconds']}s)"
                    )
                    
                    return web.json_response(
                        cached_data,
                        headers={
                            'X-Cache': 'HIT',
                            'X-Cache-TTL': str(cached_data['cache']['ttl_seconds'])
                        }
                    )
            
            # PROCESAR REQUEST (no está en caché)
            logger.info(f"🔄 Procesando nueva request: {url}")
            
            # SCRAPING DIRECTO CON AIOHTTP
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    html_content = await response.text()
                    status_code = response.status
                    headers = dict(response.headers)
            
            if not html_content:
                return web.json_response(
                    {
                        'error': 'Failed to fetch URL',
                        'url': url,
                        'status_code': status_code
                    },
                    status=500
                )
            
            # Parsear HTML
            scraping_data = self.html_parser.parse(html_content, url)
            
            # Estructura de respuesta
            response_data = {
                'url': url,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'status': 'success',
                'scraping_data': scraping_data
            }
            
            # Si se solicita procesamiento completo
            if full:
                try:
                    # PASAR HTML Y HEADERS AL SERVIDOR B
                    processing_data = await self._request_processing(
                        url,
                        html_content=html_content,
                        headers=headers
                    )
                    response_data['processing_data'] = processing_data
                except Exception as e:
                    logger.error(f"⚠️  Error en procesamiento: {e}")
                    response_data['processing_error'] = str(e)
            
            # GUARDAR EN CACHÉ
            if self.enable_cache and self.cache:
                try:
                    self.cache.set(url, response_data, full, ttl=self.cache_ttl)
                    logger.info(f"💾 Respuesta guardada en caché: {url}")
                except Exception as e:
                    logger.error(f"⚠️  Error guardando en caché: {e}")
            
            # HEADERS
            response_headers = {
                'X-Cache': 'MISS'
            }
            
            if self.enable_rate_limit and self.rate_limiter:
                try:
                    stats = self.rate_limiter.get_stats(url)
                    response_headers.update({
                        'X-RateLimit-Limit': str(stats['max_requests']),
                        'X-RateLimit-Remaining': str(stats['remaining'])
                    })
                except:
                    pass
            
            return web.json_response(response_data, headers=response_headers)
        
        except Exception as e:
            logger.error(f"❌ Error procesando request: {e}", exc_info=True)
            return web.json_response(
                {'error': 'Internal server error', 'details': str(e)},
                status=500
            )
    
    async def cache_stats_handler(self, request):
        """Endpoint para ver estadísticas de caché"""
        if not self.enable_cache or not self.cache:
            return web.json_response(
                {'error': 'Cache not enabled'},
                status=503
            )
        
        try:
            stats = self.cache.get_stats()
            return web.json_response({
                'cache_stats': stats,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        except Exception as e:
            return web.json_response(
                {'error': str(e)},
                status=500
            )
    
    async def cache_clear_handler(self, request):
        """Endpoint para limpiar toda la caché"""
        if not self.enable_cache or not self.cache:
            return web.json_response(
                {'error': 'Cache not enabled'},
                status=503
            )
        
        try:
            deleted = self.cache.clear_all()
            return web.json_response({
                'message': 'Cache cleared successfully',
                'entries_deleted': deleted,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        except Exception as e:
            return web.json_response(
                {'error': str(e)},
                status=500
            )
    
    async def _request_processing(self, url: str, html_content: str = None, headers: dict = None) -> dict:
        """
        Solicita procesamiento al Servidor B
        
        Args:
            url: URL de la página
            html_content: Contenido HTML (para análisis avanzados)
            headers: Headers HTTP (para detección de tecnologías)
        """
        try:
            logger.info(f"🔗 Conectando a {self.processing_host}:{self.processing_port}")
            
            reader, writer = await asyncio.open_connection(
                self.processing_host,
                self.processing_port
            )
            
            logger.info(f"✅ Conectado al servidor de procesamiento")
            
            # AGREGAR HTML Y HEADERS A LOS PARÁMETROS
            params = {}
            
            if html_content:
                params['html_content'] = html_content
                logger.info(f"📄 Enviando HTML ({len(html_content)} bytes)")
            
            if headers:
                params['headers'] = headers
                logger.info(f"📋 Enviando headers ({len(headers)} items)")
            
            # Crear mensaje de request
            logger.info(f"📦 Creando mensaje de request")
            message_dict = self.protocol.create_request(TaskType.ALL, url, params)
            
            # ✅ CODIFICAR EL MENSAJE A BYTES
            message_bytes = self.protocol.encode_message(message_dict)
            
            logger.info(f"📤 Enviando mensaje ({len(message_bytes)} bytes)")
            writer.write(message_bytes)
            await writer.drain()
            
            logger.info(f"⏳ Esperando respuesta...")
            response_data = await self.protocol.receive_message(reader)
            
            logger.info(f"📥 Respuesta recibida")
            
            writer.close()
            await writer.wait_closed()
            
            if response_data['type'] == MessageType.RESPONSE.value:
                logger.info(f"✅ Respuesta exitosa")
                return response_data['result']
            else:
                error_msg = response_data.get('error', 'Unknown error')
                logger.error(f"❌ Error del servidor B: {error_msg}")
                raise Exception(error_msg)
    
        except Exception as e:
            logger.error(f"❌ Error comunicándose con servidor de procesamiento: {e}", exc_info=True)
            raise
    
    async def start(self):
        """Inicia el servidor"""
        await self._init_redis_services()
        
        app = web.Application()
        
        app.router.add_get('/health', self.health_handler)
        app.router.add_get('/scrape', self.scrape_handler)
        app.router.add_get('/cache/stats', self.cache_stats_handler)
        app.router.add_post('/cache/clear', self.cache_clear_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        print("=" * 70)
        print("🚀 SERVIDOR DE SCRAPING INICIADO")
        print("=" * 70)
        print(f"📍 Dirección: http://{self.host}:{self.port}")
        print(f"🔗 Servidor de procesamiento: {self.processing_host}:{self.processing_port}")
        print(f"💡 Endpoints disponibles:")
        print(f"   - GET  /health           → Health check")
        print(f"   - GET  /scrape?url=...   → Scraping básico")
        print(f"   - GET  /scrape?url=...&full=true → Scraping completo")
        
        if self.enable_cache:
            print(f"   - GET  /cache/stats      → Estadísticas de caché")
            print(f"   - POST /cache/clear      → Limpiar caché")
        
        print(f"\n📊 Configuración:")
        print(f"   Rate Limiter: {'✅ Habilitado' if self.enable_rate_limit else '❌ Deshabilitado'}")
        if self.enable_rate_limit:
            print(f"     └─ Límite: {self.max_requests_per_minute} req/min por dominio")
        
        print(f"   Caché: {'✅ Habilitado' if self.enable_cache else '❌ Deshabilitado'}")
        if self.enable_cache:
            print(f"     └─ TTL: {self.cache_ttl}s ({self.cache_ttl//60} minutos)")
        
        if self.enable_cache or self.enable_rate_limit:
            print(f"   Redis: {self.redis_host}:{self.redis_port}")
        
        print("\n💡 Presiona Ctrl+C para detener")
        print("=" * 70)
        print()
        
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("🛑 Servidor detenido por el usuario")


def parse_arguments():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Servidor de Scraping Asíncrono con Rate Limiting y Caché'
    )
    
    parser.add_argument('-i', '--ip', default='localhost')
    parser.add_argument('-p', '--port', type=int, default=8000)
    parser.add_argument('--processing-host', default='localhost')
    parser.add_argument('--processing-port', type=int, default=9000)
    parser.add_argument('--redis-host', default='localhost')
    parser.add_argument('--redis-port', type=int, default=6379)
    parser.add_argument('--no-cache', action='store_true')
    parser.add_argument('--no-rate-limit', action='store_true')
    parser.add_argument('--max-requests', type=int, default=10)
    parser.add_argument('--cache-ttl', type=int, default=3600)
    
    return parser.parse_args()


async def main():
    """Función principal"""
    args = parse_arguments()
    
    server = ScrapingServer(
        host=args.ip,
        port=args.port,
        processing_host=args.processing_host,
        processing_port=args.processing_port,
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        enable_cache=not args.no_cache,
        enable_rate_limit=not args.no_rate_limit,
        max_requests_per_minute=args.max_requests,
        cache_ttl=args.cache_ttl
    )
    
    await server.start()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")