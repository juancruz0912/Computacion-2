"""
Analizador de SEO (Search Engine Optimization)
"""
from bs4 import BeautifulSoup
import re
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class SEOAnalyzer:
    """
    Analiza aspectos de SEO de una página web
    
    Evalúa:
    - Title tag
    - Meta description
    - Headers (H1-H6)
    - Alt tags en imágenes
    - Links internos/externos
    - Canonical URL
    - Open Graph tags
    - Structured data (JSON-LD)
    """
    
    def __init__(self):
        self.score = 100
        self.issues = []
        self.warnings = []
        self.good_practices = []
    
    def analyze(self, html_content: str, url: str) -> dict:
        """
        Analiza el SEO de una página
        
        Args:
            html_content: Contenido HTML
            url: URL de la página
        
        Returns:
            Diccionario con análisis de SEO y score
        """
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Reiniciar estado
            self.score = 100
            self.issues = []
            self.warnings = []
            self.good_practices = []
            
            # Análisis individual
            title_data = self._analyze_title(soup)
            description_data = self._analyze_meta_description(soup)
            headers_data = self._analyze_headers(soup)
            images_data = self._analyze_images(soup)
            links_data = self._analyze_links(soup, url)
            og_data = self._analyze_open_graph(soup)
            structured_data = self._analyze_structured_data(soup)
            canonical_data = self._analyze_canonical(soup, url)
            
            # Calcular grade
            grade = self._calculate_grade(self.score)
            
            result = {
                'score': max(0, self.score),
                'grade': grade,
                'title': title_data,
                'meta_description': description_data,
                'headers': headers_data,
                'images': images_data,
                'links': links_data,
                'open_graph': og_data,
                'structured_data': structured_data,
                'canonical': canonical_data,
                'issues': self.issues,
                'warnings': self.warnings,
                'good_practices': self.good_practices,
                'summary': {
                    'total_issues': len(self.issues),
                    'total_warnings': len(self.warnings),
                    'total_good_practices': len(self.good_practices)
                }
            }
            
            logger.info(
                f"✅ Análisis SEO completado: Score {self.score}/100 (Grade: {grade}), "
                f"{len(self.issues)} issues, {len(self.warnings)} warnings"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Error analizando SEO: {e}")
            return {
                'error': str(e),
                'score': 0,
                'grade': 'F'
            }
    
    def _analyze_title(self, soup: BeautifulSoup) -> dict:
        """Analiza el title tag"""
        title = soup.find('title')
        
        if not title:
            self.score -= 20
            self.issues.append("❌ CRÍTICO: Falta el tag <title>")
            return {'exists': False, 'length': 0, 'text': ''}
        
        title_text = title.get_text(strip=True)
        length = len(title_text)
        
        data = {
            'exists': True,
            'text': title_text,
            'length': length
        }
        
        # Evaluación
        if length == 0:
            self.score -= 20
            self.issues.append("❌ CRÍTICO: El <title> está vacío")
        elif length < 30:
            self.score -= 10
            self.warnings.append(f"⚠️  Title muy corto ({length} chars). Recomendado: 50-60")
        elif length > 60:
            self.score -= 5
            self.warnings.append(f"⚠️  Title muy largo ({length} chars). Recomendado: 50-60")
        else:
            self.good_practices.append(f"✅ Title con longitud óptima ({length} chars)")
        
        return data
    
    def _analyze_meta_description(self, soup: BeautifulSoup) -> dict:
        """Analiza la meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        
        if not meta_desc or not meta_desc.get('content'):
            self.score -= 15
            self.issues.append("❌ Falta meta description")
            return {'exists': False, 'length': 0, 'text': ''}
        
        description = meta_desc.get('content', '').strip()
        length = len(description)
        
        data = {
            'exists': True,
            'text': description,
            'length': length
        }
        
        # Evaluación
        if length < 120:
            self.score -= 5
            self.warnings.append(f"⚠️  Meta description corta ({length} chars). Recomendado: 150-160")
        elif length > 160:
            self.score -= 3
            self.warnings.append(f"⚠️  Meta description larga ({length} chars). Será truncada en resultados")
        else:
            self.good_practices.append(f"✅ Meta description con longitud óptima ({length} chars)")
        
        return data
    
    def _analyze_headers(self, soup: BeautifulSoup) -> dict:
        """Analiza los headers H1-H6"""
        h1_tags = soup.find_all('h1')
        h1_count = len(h1_tags)
        
        data = {
            'h1_count': h1_count,
            'h1_texts': [h1.get_text(strip=True)[:100] for h1 in h1_tags[:3]],
            'hierarchy': {
                'h1': h1_count,
                'h2': len(soup.find_all('h2')),
                'h3': len(soup.find_all('h3')),
                'h4': len(soup.find_all('h4')),
                'h5': len(soup.find_all('h5')),
                'h6': len(soup.find_all('h6'))
            }
        }
        
        # Evaluación de H1
        if h1_count == 0:
            self.score -= 15
            self.issues.append("❌ No hay ningún tag <h1>")
        elif h1_count > 1:
            self.score -= 10
            self.warnings.append(f"⚠️  Múltiples H1 detectados ({h1_count}). Recomendado: 1 único H1")
        else:
            self.good_practices.append("✅ Un único H1 correctamente definido")
        
        # Verificar jerarquía
        if data['hierarchy']['h2'] == 0 and any(data['hierarchy'][f'h{i}'] > 0 for i in range(3, 7)):
            self.warnings.append("⚠️  Jerarquía de headers incorrecta (hay H3+ sin H2)")
        
        return data
    
    def _analyze_images(self, soup: BeautifulSoup) -> dict:
        """Analiza imágenes y alt tags"""
        images = soup.find_all('img')
        total_images = len(images)
        
        images_without_alt = [
            img for img in images 
            if not img.get('alt') or not img.get('alt').strip()
        ]
        
        missing_alt_count = len(images_without_alt)
        
        data = {
            'total_images': total_images,
            'images_without_alt': missing_alt_count,
            'alt_coverage_percent': round(
                ((total_images - missing_alt_count) / total_images * 100) if total_images > 0 else 100,
                2
            )
        }
        
        # Evaluación
        if missing_alt_count > 0:
            penalty = min(20, missing_alt_count * 2)
            self.score -= penalty
            
            if missing_alt_count <= 3:
                self.warnings.append(
                    f"⚠️  {missing_alt_count} imagen(es) sin atributo alt"
                )
            else:
                self.issues.append(
                    f"❌ {missing_alt_count} imágenes sin atributo alt (afecta accesibilidad y SEO)"
                )
        elif total_images > 0:
            self.good_practices.append(f"✅ Todas las imágenes ({total_images}) tienen alt text")
        
        return data
    
    def _analyze_links(self, soup: BeautifulSoup, base_url: str) -> dict:
        """Analiza links internos y externos"""
        links = soup.find_all('a', href=True)
        
        internal_links = []
        external_links = []
        broken_links = []
        
        base_domain = self._get_domain(base_url)
        
        for link in links:
            href = link.get('href', '').strip()
            
            if href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            if href.startswith('http'):
                link_domain = self._get_domain(href)
                
                if link_domain == base_domain:
                    internal_links.append(href)
                else:
                    external_links.append(href)
            else:
                internal_links.append(href)
        
        data = {
            'total_links': len(links),
            'internal_links': len(internal_links),
            'external_links': len(external_links),
            'ratio': round(
                len(internal_links) / len(links) if len(links) > 0 else 0,
                2
            )
        }
        
        # Evaluación
        if len(links) == 0:
            self.warnings.append("⚠️  No se encontraron links en la página")
        elif len(internal_links) == 0:
            self.warnings.append("⚠️  No hay links internos (mal para SEO)")
        else:
            self.good_practices.append(
                f"✅ Balance de links: {len(internal_links)} internos, {len(external_links)} externos"
            )
        
        return data
    
    def _analyze_open_graph(self, soup: BeautifulSoup) -> dict:
        """Analiza Open Graph tags"""
        og_tags = {}
        
        for meta in soup.find_all('meta', property=True):
            prop = meta.get('property', '')
            if prop.startswith('og:'):
                key = prop.replace('og:', '')
                og_tags[key] = meta.get('content', '')
        
        required_tags = ['title', 'description', 'image', 'url']
        missing_tags = [tag for tag in required_tags if tag not in og_tags]
        
        data = {
            'exists': len(og_tags) > 0,
            'tags': og_tags,
            'missing_required': missing_tags,
            'completeness_percent': round(
                ((len(required_tags) - len(missing_tags)) / len(required_tags) * 100),
                2
            )
        }
        
        # Evaluación
        if len(og_tags) == 0:
            self.warnings.append("⚠️  No hay tags Open Graph (recomendados para redes sociales)")
        elif len(missing_tags) > 0:
            self.warnings.append(
                f"⚠️  Faltan Open Graph tags: {', '.join(missing_tags)}"
            )
        else:
            self.good_practices.append("✅ Open Graph tags completos")
        
        return data
    
    def _analyze_structured_data(self, soup: BeautifulSoup) -> dict:
        """Analiza datos estructurados (JSON-LD, Schema.org)"""
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        structured_data = {
            'has_json_ld': len(json_ld_scripts) > 0,
            'json_ld_count': len(json_ld_scripts),
            'types': []
        }
        
        # Extraer tipos de schema
        for script in json_ld_scripts:
            try:
                import json
                data = json.loads(script.string)
                
                if isinstance(data, dict) and '@type' in data:
                    structured_data['types'].append(data['@type'])
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and '@type' in item:
                            structured_data['types'].append(item['@type'])
            except:
                pass
        
        # Evaluación
        if structured_data['has_json_ld']:
            self.good_practices.append(
                f"✅ Datos estructurados presentes ({len(json_ld_scripts)} schemas)"
            )
        else:
            self.warnings.append(
                "⚠️  No hay datos estructurados (JSON-LD recomendado para SEO avanzado)"
            )
        
        return structured_data
    
    def _analyze_canonical(self, soup: BeautifulSoup, url: str) -> dict:
        """Analiza canonical URL"""
        canonical = soup.find('link', rel='canonical')
        
        data = {
            'exists': canonical is not None,
            'url': canonical.get('href') if canonical else None
        }
        
        # Evaluación
        if not data['exists']:
            self.warnings.append("⚠️  Falta tag canonical (puede causar contenido duplicado)")
        else:
            self.good_practices.append("✅ Tag canonical presente")
        
        return data
    
    def _get_domain(self, url: str) -> str:
        """Extrae el dominio de una URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    
    def _calculate_grade(self, score: int) -> str:
        """Calcula el grade basado en el score"""
        if score >= 90:
            return 'A'
        elif score >= 75:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 45:
            return 'D'
        else:
            return 'F'


def analyze_seo(html_content: str, url: str) -> dict:
    """
    Función helper para analizar SEO
    
    Args:
        html_content: Contenido HTML
        url: URL de la página
    
    Returns:
        Diccionario con análisis de SEO
    """
    analyzer = SEOAnalyzer()
    return analyzer.analyze(html_content, url)