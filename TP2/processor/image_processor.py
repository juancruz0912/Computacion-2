import logging
import io
import base64
import asyncio
import aiohttp
from typing import Dict, List
from datetime import datetime
from PIL import Image
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Procesador de imágenes web"""
    
    def __init__(self, max_concurrent: int = 5, timeout: int = 10):
        """
        Inicializar el procesador
        
        Args:
            max_concurrent: Máximo de descargas concurrentes
            timeout: Timeout para descargar imágenes
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout
    
    async def download_image(self, url: str, session: aiohttp.ClientSession) -> bytes:
        """
        Descargar una imagen
        
        Args:
            url: URL de la imagen
            session: Sesión de aiohttp
            
        Returns:
            Bytes de la imagen
        """
        try:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    logger.warning(f"⚠️  HTTP {response.status} descargando {url}")
                    return b''
        except Exception as e:
            logger.error(f"❌ Error descargando {url}: {e}")
            return b''
    
    async def process_images(self, image_urls: List[str], create_thumbnails: bool = True) -> Dict:
        """
        Procesar múltiples imágenes
        
        Args:
            image_urls: Lista de URLs de imágenes
            create_thumbnails: Si crear thumbnails
            
        Returns:
            Diccionario con imágenes procesadas
        """
        logger.info(f"🖼️  Procesando {len(image_urls)} imágenes")
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Descargar imágenes en paralelo (limitado)
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def download_with_limit(url):
                async with semaphore:
                    return await self.download_image(url, session)
            
            tasks = [download_with_limit(url) for url in image_urls]
            images_data = await asyncio.gather(*tasks)
        
        # Procesar cada imagen
        processed_images = []
        
        for url, img_data in zip(image_urls, images_data):
            if not img_data:
                continue
            
            try:
                result = self._process_single_image(url, img_data, create_thumbnails)
                processed_images.append(result)
            except Exception as e:
                logger.error(f"❌ Error procesando {url}: {e}")
        
        logger.info(f"✅ Procesadas {len(processed_images)} imágenes")
        
        return {
            'total_requested': len(image_urls),
            'total_processed': len(processed_images),
            'images': processed_images,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def _process_single_image(self, url: str, img_data: bytes, create_thumbnail: bool) -> Dict:
        """
        Procesar una sola imagen
        
        Args:
            url: URL de la imagen
            img_data: Bytes de la imagen
            create_thumbnail: Si crear thumbnail
            
        Returns:
            Diccionario con imagen procesada
        """
        # Abrir imagen
        img = Image.open(io.BytesIO(img_data))
        
        # Información básica
        result = {
            'url': url,
            'format': img.format,
            'mode': img.mode,
            'dimensions': {
                'width': img.width,
                'height': img.height
            },
            'size_bytes': len(img_data),
            'size_kb': round(len(img_data) / 1024, 2)
        }
        
        # Crear thumbnail si se solicita
        if create_thumbnail:
            thumb_data = self._create_thumbnail(img)
            result['thumbnail'] = thumb_data
        
        return result
    
    def _create_thumbnail(self, img: Image.Image, max_size: int = 200) -> Dict:
        """
        Crear thumbnail de una imagen
        
        Args:
            img: Imagen PIL
            max_size: Tamaño máximo del thumbnail
            
        Returns:
            Diccionario con thumbnail
        """
        # Crear copia para thumbnail
        thumb = img.copy()
        
        # Calcular dimensiones manteniendo aspect ratio
        aspect_ratio = thumb.height / thumb.width
        
        if thumb.width > thumb.height:
            thumb_width = max_size
            thumb_height = int(max_size * aspect_ratio)
        else:
            thumb_height = max_size
            thumb_width = int(max_size / aspect_ratio)
        
        # Redimensionar
        thumb.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        
        # Convertir a bytes
        thumb_buffer = io.BytesIO()
        thumb.save(thumb_buffer, format='PNG')
        thumb_bytes = thumb_buffer.getvalue()
        
        # Codificar en base64
        thumb_b64 = base64.b64encode(thumb_bytes).decode('ascii')
        
        return {
            'thumbnail_base64': thumb_b64,
            'format': 'png',
            'dimensions': {
                'width': thumb.width,
                'height': thumb.height
            },
            'size_bytes': len(thumb_bytes),
            'size_kb': round(len(thumb_bytes) / 1024, 2)
        }
    
    def optimize_image(self, img_data: bytes, quality: int = 85, max_width: int = 1920) -> bytes:
        """
        Optimizar una imagen (comprimir y redimensionar si es necesario)
        
        Args:
            img_data: Bytes de la imagen
            quality: Calidad de compresión (1-100)
            max_width: Ancho máximo
            
        Returns:
            Bytes de la imagen optimizada
        """
        img = Image.open(io.BytesIO(img_data))
        
        # Redimensionar si es muy grande
        if img.width > max_width:
            aspect_ratio = img.height / img.width
            new_height = int(max_width * aspect_ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Guardar con compresión
        output = io.BytesIO()
        
        if img.format in ('JPEG', 'JPG'):
            img.save(output, format='JPEG', quality=quality, optimize=True)
        elif img.format == 'PNG':
            img.save(output, format='PNG', optimize=True)
        else:
            img.save(output, format=img.format)
        
        return output.getvalue()