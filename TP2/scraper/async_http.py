"""
Cliente HTTP asíncrono para realizar scraping web
"""

import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class AsyncHttpClient:
    """Cliente HTTP asíncrono optimizado para scraping"""
    
    def __init__(self, timeout: int = 30, max_concurrent: int = 10):
        """
        Inicializar el cliente HTTP
        
        Args:
            timeout: Timeout en segundos para requests
            max_concurrent: Máximo de conexiones concurrentes
        """
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Headers por defecto para evitar bloqueos
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    async def fetch(self, url: str, headers: Optional[Dict] = None) -> Tuple[int, str, Dict]:
        """
        Realizar un GET request asíncrono
        
        Args:
            url: URL a descargar
            headers: Headers HTTP opcionales
            
        Returns:
            Tupla (status_code, html_content, response_headers)
            
        Raises:
            aiohttp.ClientError: Si hay error de red
            asyncio.TimeoutError: Si excede el timeout
        """
        async with self.semaphore:  # Limitar concurrencia
            
            # Combinar headers
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                logger.info(f"📥 Descargando: {url}")
                
                try:
                    async with session.get(url, headers=request_headers, allow_redirects=True) as response:
                        status = response.status
                        content = await response.text()
                        response_headers = dict(response.headers)
                        
                        logger.info(f"✅ {url} - Status: {status} - Size: {len(content)} bytes")
                        
                        return status, content, response_headers
                
                except asyncio.TimeoutError:
                    logger.error(f"⏱️  Timeout descargando {url}")
                    raise
                
                except aiohttp.ClientError as e:
                    logger.error(f"❌ Error descargando {url}: {e}")
                    raise
    
    async def fetch_multiple(self, urls: list[str]) -> Dict[str, Tuple[int, str, Dict]]:
        """
        Descargar múltiples URLs en paralelo
        
        Args:
            urls: Lista de URLs
            
        Returns:
            Diccionario {url: (status, content, headers)}
        """
        tasks = [self.fetch(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            url: result if not isinstance(result, Exception) else (0, str(result), {})
            for url, result in zip(urls, results)
        }
    
    async def download_binary(self, url: str) -> bytes:
        """
        Descargar contenido binario (imágenes, PDFs, etc.)
        
        Args:
            url: URL del recurso
            
        Returns:
            Contenido binario
        """
        async with self.semaphore:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                logger.info(f"📥 Descargando binario: {url}")
                
                async with session.get(url, headers=self.default_headers) as response:
                    if response.status != 200:
                        raise aiohttp.ClientError(f"HTTP {response.status}")
                    
                    content = await response.read()
                    logger.info(f"✅ Descargado: {len(content)} bytes")
                    
                    return content