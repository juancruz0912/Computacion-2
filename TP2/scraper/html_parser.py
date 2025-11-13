"""
Parser HTML para extraer información estructurada de páginas web
"""
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)


class HtmlParser:
    """
    Parser de HTML usando BeautifulSoup
    
    Extrae:
    - Título y texto
    - Estructura (headers, elementos)
    - Links e imágenes
    - Metadatos (SEO, Open Graph, Twitter Cards)
    """
    
    def __init__(self):
        self.parser = 'lxml'  # Usar lxml para mejor performance
    
    def parse(self, html_content: str, base_url: str) -> dict:
        """
        Parsea contenido HTML y extrae información estructurada
        
        Args:
            html_content: Contenido HTML como string
            base_url: URL base para resolver links relativos
        
        Returns:
            Diccionario con datos extraídos
        """
        try:
            soup = BeautifulSoup(html_content, self.parser)
            
            return {
                'basic': self._extract_basic_info(soup),
                'structure': self._extract_structure(soup),
                'links': self._extract_links(soup, base_url),
                'images': self._extract_images(soup, base_url),
                'metadata': self._extract_metadata(soup)
            }
        
        except Exception as e:
            logger.error(f"Error parseando HTML: {e}")
            return {
                'error': str(e),
                'basic': {},
                'structure': {},
                'links': [],
                'images': [],
                'metadata': {}
            }
    
    def _extract_basic_info(self, soup: BeautifulSoup) -> dict:
        """Extrae información básica de la página"""
        try:
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else 'Sin título'
            
            # Extraer todo el texto visible
            for script in soup(['script', 'style']):
                script.decompose()
            
            text = soup.get_text(separator=' ', strip=True)
            words = text.split()
            
            return {
                'title': title_text,
                'text_preview': ' '.join(words[:50]),  # Primeras 50 palabras
                'word_count': len(words)
            }
        
        except Exception as e:
            logger.error(f"Error extrayendo info básica: {e}")
            return {}
    
    def _extract_structure(self, soup: BeautifulSoup) -> dict:
        """Extrae estructura de la página"""
        try:
            return {
                'headers': {
                    'h1': len(soup.find_all('h1')),
                    'h2': len(soup.find_all('h2')),
                    'h3': len(soup.find_all('h3')),
                    'h4': len(soup.find_all('h4')),
                    'h5': len(soup.find_all('h5')),
                    'h6': len(soup.find_all('h6'))
                },
                'elements_count': {
                    'paragraphs': len(soup.find_all('p')),
                    'links': len(soup.find_all('a')),
                    'images': len(soup.find_all('img')),
                    'lists': len(soup.find_all(['ul', 'ol'])),
                    'tables': len(soup.find_all('table'))
                }
            }
        
        except Exception as e:
            logger.error(f"Error extrayendo estructura: {e}")
            return {}
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extrae todos los links de la página"""
        try:
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').strip()
                
                if not href or href.startswith(('#', 'javascript:', 'mailto:')):
                    continue
                
                # Convertir links relativos a absolutos
                absolute_url = urljoin(base_url, href)
                
                links.append({
                    'url': absolute_url,
                    'text': link.get_text(strip=True)[:100]  # Max 100 chars
                })
            
            return links[:100]  # Limitar a 100 links
        
        except Exception as e:
            logger.error(f"Error extrayendo links: {e}")
            return []
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> list:
        """Extrae información de imágenes"""
        try:
            images = []
            
            for img in soup.find_all('img'):
                src = img.get('src', '').strip()
                
                if not src:
                    continue
                
                # Convertir a URL absoluta
                absolute_url = urljoin(base_url, src)
                
                images.append({
                    'url': absolute_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                })
            
            return images[:50]  # Limitar a 50 imágenes
        
        except Exception as e:
            logger.error(f"Error extrayendo imágenes: {e}")
            return []
    
    def _extract_metadata(self, soup: BeautifulSoup) -> dict:
        """Extrae metadatos (meta tags, Open Graph, Twitter Cards)"""
        try:
            metadata = {
                'basic': {},
                'open_graph': {},
                'twitter': {}
            }
            
            # Meta tags básicos
            for meta in soup.find_all('meta'):
                name = meta.get('name', '').lower()
                property_attr = meta.get('property', '').lower()
                content = meta.get('content', '')
                
                # Meta tags básicos
                if name in ['description', 'keywords', 'author', 'viewport']:
                    metadata['basic'][name] = content
                
                # Open Graph
                if property_attr.startswith('og:'):
                    key = property_attr.replace('og:', '')
                    metadata['open_graph'][key] = content
                
                # Twitter Cards
                if name.startswith('twitter:'):
                    key = name.replace('twitter:', '')
                    metadata['twitter'][key] = content
            
            return metadata
        
        except Exception as e:
            logger.error(f"Error extrayendo metadata: {e}")
            return {}