"""
Extractor de metadatos de páginas web
"""

from bs4 import BeautifulSoup
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extractor de metadatos y meta tags"""
    
    def __init__(self, html: str):
        """
        Inicializar el extractor
        
        Args:
            html: Contenido HTML
        """
        self.soup = BeautifulSoup(html, 'html.parser')
    
    def extract_all(self) -> Dict:
        """
        Extraer todos los metadatos disponibles
        
        Returns:
            Diccionario con todos los metadatos
        """
        return {
            'basic': self.extract_basic_meta(),
            'open_graph': self.extract_open_graph(),
            'twitter': self.extract_twitter_cards(),
            'seo': self.extract_seo_tags()
        }
    
    def extract_basic_meta(self) -> Dict[str, str]:
        """
        Extraer meta tags básicos
        
        Returns:
            Diccionario con meta tags básicos
        """
        meta_tags = {}
        
        # Meta tags comunes
        common_names = [
            'description', 'keywords', 'author', 'viewport',
            'robots', 'googlebot', 'charset', 'language'
        ]
        
        for name in common_names:
            tag = self.soup.find('meta', attrs={'name': name})
            if tag and tag.get('content'):
                meta_tags[name] = tag['content']
        
        # Charset
        charset_tag = self.soup.find('meta', charset=True)
        if charset_tag:
            meta_tags['charset'] = charset_tag.get('charset', '')
        
        return meta_tags
    
    def extract_open_graph(self) -> Dict[str, str]:
        """
        Extraer Open Graph meta tags (Facebook)
        
        Returns:
            Diccionario con tags Open Graph
        """
        og_tags = {}
        
        og_properties = [
            'og:title', 'og:description', 'og:image', 'og:url',
            'og:type', 'og:site_name', 'og:locale'
        ]
        
        for prop in og_properties:
            tag = self.soup.find('meta', property=prop)
            if tag and tag.get('content'):
                # Remover el prefijo 'og:'
                key = prop.replace('og:', '')
                og_tags[key] = tag['content']
        
        return og_tags
    
    def extract_twitter_cards(self) -> Dict[str, str]:
        """
        Extraer Twitter Card meta tags
        
        Returns:
            Diccionario con Twitter Card tags
        """
        twitter_tags = {}
        
        twitter_properties = [
            'twitter:card', 'twitter:site', 'twitter:creator',
            'twitter:title', 'twitter:description', 'twitter:image'
        ]
        
        for prop in twitter_properties:
            tag = self.soup.find('meta', attrs={'name': prop})
            if tag and tag.get('content'):
                # Remover el prefijo 'twitter:'
                key = prop.replace('twitter:', '')
                twitter_tags[key] = tag['content']
        
        return twitter_tags
    
    def extract_seo_tags(self) -> Dict:
        """
        Extraer tags relacionados con SEO
        
        Returns:
            Diccionario con información de SEO
        """
        seo_info = {}
        
        # Canonical URL
        canonical = self.soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            seo_info['canonical'] = canonical['href']
        
        # Alternate languages
        alternates = self.soup.find_all('link', rel='alternate', hreflang=True)
        if alternates:
            seo_info['alternates'] = [
                {
                    'hreflang': alt.get('hreflang'),
                    'href': alt.get('href')
                }
                for alt in alternates
            ]
        
        # Robots meta
        robots = self.soup.find('meta', attrs={'name': 'robots'})
        if robots and robots.get('content'):
            seo_info['robots'] = robots['content']
        
        return seo_info
    
    def extract_favicon(self) -> Optional[str]:
        """
        Extraer la URL del favicon
        
        Returns:
            URL del favicon o None
        """
        # Buscar diferentes tipos de favicon
        favicon_rels = [
            'icon', 'shortcut icon', 'apple-touch-icon',
            'apple-touch-icon-precomposed'
        ]
        
        for rel in favicon_rels:
            tag = self.soup.find('link', rel=rel)
            if tag and tag.get('href'):
                return tag['href']
        
        return None
    
    def extract_structured_data(self) -> List[Dict]:
        """
        Extraer datos estructurados (JSON-LD, Microdata, etc.)
        
        Returns:
            Lista de objetos de datos estructurados
        """
        structured_data = []
        
        # JSON-LD
        for script in self.soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(script.string)
                structured_data.append({
                    'type': 'json-ld',
                    'data': data
                })
            except Exception as e:
                logger.warning(f"Error parsing JSON-LD: {e}")
        
        return structured_data