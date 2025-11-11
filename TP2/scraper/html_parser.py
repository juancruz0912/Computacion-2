"""
Funciones para parsear y extraer información de HTML
"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class HtmlParser:
    """Parser de HTML para extraer información estructurada"""
    
    def __init__(self, html: str, base_url: str):
        """
        Inicializar el parser
        
        Args:
            html: Contenido HTML como string
            base_url: URL base para resolver enlaces relativos
        """
        self.html = html
        self.base_url = base_url
        self.soup = BeautifulSoup(html, 'html.parser')
    
    def extract_title(self) -> str:
        """
        Extraer el título de la página
        
        Returns:
            Título de la página o mensaje si no existe
        """
        title_tag = self.soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        # Intentar con og:title
        og_title = self.soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content']
        
        return 'Sin título'
    
    def extract_headers(self) -> Dict[str, int]:
        """
        Extraer la estructura de headers (H1-H6)
        
        Returns:
            Diccionario con conteo de cada tipo de header
        """
        headers = {}
        for i in range(1, 7):
            tag = f'h{i}'
            count = len(self.soup.find_all(tag))
            headers[tag] = count
        
        return headers
    
    def extract_headers_content(self) -> Dict[str, List[str]]:
        """
        Extraer el contenido de los headers
        
        Returns:
            Diccionario con listas del contenido de cada header
        """
        headers_content = {}
        for i in range(1, 7):
            tag = f'h{i}'
            headers = self.soup.find_all(tag)
            headers_content[tag] = [h.get_text(strip=True) for h in headers]
        
        return headers_content
    
    def extract_links(self, limit: int = 50) -> List[str]:
        """
        Extraer todos los enlaces de la página
        
        Args:
            limit: Número máximo de enlaces a retornar
            
        Returns:
            Lista de URLs absolutas únicas
        """
        links = []
        
        for a_tag in self.soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Resolver URL relativa a absoluta
            absolute_url = urljoin(self.base_url, href)
            
            # Validar que sea una URL HTTP/HTTPS
            parsed = urlparse(absolute_url)
            if parsed.scheme in ('http', 'https'):
                links.append(absolute_url)
        
        # Eliminar duplicados manteniendo el orden
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        return unique_links[:limit]
    
    def extract_images(self, limit: int = 20) -> List[Dict[str, str]]:
        """
        Extraer información de imágenes
        
        Args:
            limit: Número máximo de imágenes
            
        Returns:
            Lista de diccionarios con info de cada imagen
        """
        images = []
        
        for img_tag in self.soup.find_all('img'):
            src = img_tag.get('src')
            if not src:
                continue
            
            # Resolver URL absoluta
            absolute_url = urljoin(self.base_url, src)
            
            image_info = {
                'url': absolute_url,
                'alt': img_tag.get('alt', ''),
                'title': img_tag.get('title', ''),
                'width': img_tag.get('width', ''),
                'height': img_tag.get('height', '')
            }
            
            images.append(image_info)
            
            if len(images) >= limit:
                break
        
        return images
    
    def count_elements(self) -> Dict[str, int]:
        """
        Contar diferentes elementos HTML
        
        Returns:
            Diccionario con conteos
        """
        return {
            'paragraphs': len(self.soup.find_all('p')),
            'images': len(self.soup.find_all('img')),
            'links': len(self.soup.find_all('a')),
            'lists': len(self.soup.find_all(['ul', 'ol'])),
            'tables': len(self.soup.find_all('table')),
            'forms': len(self.soup.find_all('form')),
            'divs': len(self.soup.find_all('div')),
            'spans': len(self.soup.find_all('span'))
        }
    
    def extract_text_content(self, max_length: int = 500) -> str:
        """
        Extraer el texto principal de la página
        
        Args:
            max_length: Longitud máxima del texto
            
        Returns:
            Texto extraído
        """
        # Eliminar scripts y estilos
        for script in self.soup(['script', 'style']):
            script.decompose()
        
        # Obtener texto
        text = self.soup.get_text(separator=' ', strip=True)
        
        # Limitar longitud
        if len(text) > max_length:
            text = text[:max_length] + '...'
        
        return text