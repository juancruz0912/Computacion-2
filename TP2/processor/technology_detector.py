"""
Detector de tecnologías web (frameworks, CMS, librerías, servidores)
"""
from bs4 import BeautifulSoup
import re
import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class TechnologyDetector:
    """
    Detecta tecnologías utilizadas en una página web
    
    Categorías:
    - Frameworks JavaScript (React, Vue, Angular, etc.)
    - CMS (WordPress, Drupal, Joomla, etc.)
    - Librerías JavaScript (jQuery, Bootstrap, etc.)
    - Analytics (Google Analytics, Facebook Pixel, etc.)
    - Servidores web
    - CDNs
    """
    
    def __init__(self):
        # Patrones de detección
        self.patterns = {
            'frameworks': {
                'React': [
                    r'react\.min\.js',
                    r'react-dom',
                    r'data-reactroot',
                    r'_react',
                    r'__REACT'
                ],
                'Vue.js': [
                    r'vue\.min\.js',
                    r'vue\.js',
                    r'data-v-',
                    r'__VUE',
                    r'v-bind',
                    r'v-if',
                    r'v-for'
                ],
                'Angular': [
                    r'angular\.min\.js',
                    r'ng-app',
                    r'ng-controller',
                    r'ng-model',
                    r'angular\.io'
                ],
                'Next.js': [
                    r'_next/',
                    r'__NEXT_DATA__',
                    r'next\.js'
                ],
                'Nuxt.js': [
                    r'_nuxt/',
                    r'__NUXT__'
                ],
                'Svelte': [
                    r'svelte\.js',
                    r'class="svelte-'
                ],
                'Ember.js': [
                    r'ember\.min\.js',
                    r'ember-application'
                ]
            },
            'cms': {
                'WordPress': [
                    r'wp-content/',
                    r'wp-includes/',
                    r'/wp-json/',
                    r'wordpress',
                    r'wp-embed\.min\.js'
                ],
                'Drupal': [
                    r'drupal',
                    r'/sites/default/',
                    r'Drupal\.settings'
                ],
                'Joomla': [
                    r'joomla',
                    r'/components/com_',
                    r'option=com_'
                ],
                'Shopify': [
                    r'cdn\.shopify\.com',
                    r'myshopify\.com',
                    r'Shopify\.theme'
                ],
                'Wix': [
                    r'wix\.com',
                    r'parastorage\.com'
                ],
                'Squarespace': [
                    r'squarespace',
                    r'static1\.squarespace'
                ],
                'Magento': [
                    r'magento',
                    r'Mage\.Cookies'
                ],
                'PrestaShop': [
                    r'prestashop',
                    r'/modules/prestashop'
                ]
            },
            'libraries': {
                'jQuery': [
                    r'jquery\.min\.js',
                    r'jquery-[0-9]',
                    r'\$\.ajax'
                ],
                'Bootstrap': [
                    r'bootstrap\.min\.js',
                    r'bootstrap\.css',
                    r'class="[^"]*\bbtn\b',
                    r'class="[^"]*\bcontainer\b'
                ],
                'Tailwind CSS': [
                    r'tailwindcss',
                    r'class="[^"]*\bflex\b',
                    r'class="[^"]*\bgrid\b'
                ],
                'Font Awesome': [
                    r'font-awesome',
                    r'fa-',
                    r'fontawesome'
                ],
                'Lodash': [
                    r'lodash\.min\.js',
                    r'_.debounce'
                ],
                'Moment.js': [
                    r'moment\.min\.js',
                    r'moment\.js'
                ],
                'Chart.js': [
                    r'chart\.min\.js',
                    r'Chart\.js'
                ],
                'Three.js': [
                    r'three\.min\.js',
                    r'THREE\.'
                ]
            },
            'analytics': {
                'Google Analytics': [
                    r'google-analytics\.com',
                    r'gtag\.js',
                    r'ga\.js',
                    r'analytics\.js'
                ],
                'Google Tag Manager': [
                    r'googletagmanager\.com',
                    r'gtm\.js'
                ],
                'Facebook Pixel': [
                    r'facebook\.com/tr',
                    r'fbq\(',
                    r'connect\.facebook\.net'
                ],
                'Hotjar': [
                    r'hotjar\.com',
                    r'_hjSettings'
                ],
                'Mixpanel': [
                    r'mixpanel\.com',
                    r'mixpanel\.init'
                ],
                'Segment': [
                    r'segment\.com',
                    r'analytics\.load'
                ]
            }
        }
    
    def analyze(self, html_content: str, headers: dict = None) -> dict:
        """
        Analiza el HTML y headers para detectar tecnologías
        
        Args:
            html_content: Contenido HTML de la página
            headers: Headers HTTP de la respuesta
        
        Returns:
            Diccionario con tecnologías detectadas por categoría
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Convertir HTML a string para búsquedas de patrones
            html_str = str(soup).lower()
            
            detected = {
                'frameworks': [],
                'cms': [],
                'libraries': [],
                'analytics': [],
                'servers': [],
                'meta': {}
            }
            
            # Detectar por patrones en HTML
            for category, technologies in self.patterns.items():
                for tech_name, patterns in technologies.items():
                    if self._match_patterns(html_str, patterns):
                        detected[category].append(tech_name)
            
            # Detectar servidor web desde headers
            if headers:
                detected['servers'] = self._detect_servers(headers)
            
            # Detectar generadores desde meta tags
            detected['meta'] = self._detect_meta_generators(soup)
            
            # Remover duplicados y ordenar
            for key in detected:
                if isinstance(detected[key], list):
                    detected[key] = sorted(list(set(detected[key])))
            
            # Agregar resumen
            total_detected = sum(
                len(v) for k, v in detected.items() 
                if isinstance(v, list)
            )
            
            detected['summary'] = {
                'total_technologies': total_detected,
                'categories': {
                    'frameworks': len(detected['frameworks']),
                    'cms': len(detected['cms']),
                    'libraries': len(detected['libraries']),
                    'analytics': len(detected['analytics']),
                    'servers': len(detected['servers'])
                }
            }
            
            logger.info(
                f"✅ Tecnologías detectadas: {total_detected} "
                f"({', '.join(f'{k}: {v}' for k, v in detected['summary']['categories'].items())})"
            )
            
            return detected
        
        except Exception as e:
            logger.error(f"❌ Error detectando tecnologías: {e}")
            return {
                'error': str(e),
                'frameworks': [],
                'cms': [],
                'libraries': [],
                'analytics': [],
                'servers': [],
                'meta': {},
                'summary': {'total_technologies': 0}
            }
    
    def _match_patterns(self, text: str, patterns: List[str]) -> bool:
        """Verifica si algún patrón coincide en el texto"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _detect_servers(self, headers: dict) -> List[str]:
        """Detecta servidor web desde headers HTTP"""
        servers = []
        
        server_header = headers.get('server', '').lower()
        x_powered_by = headers.get('x-powered-by', '').lower()
        
        # Detectar servidor web
        if 'nginx' in server_header:
            servers.append('Nginx')
        elif 'apache' in server_header:
            servers.append('Apache')
        elif 'cloudflare' in server_header:
            servers.append('Cloudflare')
        elif 'microsoft-iis' in server_header:
            servers.append('Microsoft IIS')
        elif 'litespeed' in server_header:
            servers.append('LiteSpeed')
        
        # Detectar tecnologías del backend
        if 'php' in x_powered_by:
            servers.append('PHP')
        elif 'asp.net' in x_powered_by:
            servers.append('ASP.NET')
        elif 'express' in x_powered_by:
            servers.append('Express.js')
        
        return servers
    
    def _detect_meta_generators(self, soup: BeautifulSoup) -> dict:
        """Detecta generadores desde meta tags"""
        meta_info = {}
        
        # Meta generator
        generator = soup.find('meta', attrs={'name': 'generator'})
        if generator and generator.get('content'):
            meta_info['generator'] = generator.get('content')
        
        # Application name
        app_name = soup.find('meta', attrs={'name': 'application-name'})
        if app_name and app_name.get('content'):
            meta_info['application_name'] = app_name.get('content')
        
        # Theme
        theme = soup.find('meta', attrs={'name': 'theme'})
        if theme and theme.get('content'):
            meta_info['theme'] = theme.get('content')
        
        return meta_info


def detect_technologies(html_content: str, headers: dict = None) -> dict:
    """
    Función helper para detectar tecnologías
    
    Args:
        html_content: Contenido HTML
        headers: Headers HTTP
    
    Returns:
        Diccionario con tecnologías detectadas
    """
    detector = TechnologyDetector()
    return detector.analyze(html_content, headers)