import logging
import time
from typing import Dict, List
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """Analizador de métricas de rendimiento web"""
    
    def __init__(self, headless: bool = True):
        """
        Inicializar el analizador
        
        Args:
            headless: Ejecutar en modo headless
        """
        self.headless = headless
    
    def _create_driver(self) -> webdriver.Chrome:
        """Crear WebDriver configurado"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # Habilitar logging de rendimiento
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        return driver
    
    def analyze(self, url: str) -> Dict:
        """
        Analizar rendimiento de una URL
        
        Args:
            url: URL a analizar
            
        Returns:
            Diccionario con métricas de rendimiento
        """
        driver = None
        
        try:
            logger.info(f"📊 Analizando rendimiento de {url}")
            
            driver = self._create_driver()
            
            # Medir tiempo de carga
            start_time = time.time()
            driver.get(url)
            
            # Esperar a que cargue completamente
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            end_time = time.time()
            page_load_time = round((end_time - start_time) * 1000, 2)  # en ms
            
            # Obtener métricas de navegación usando JavaScript
            navigation_timing = driver.execute_script("""
                var timing = window.performance.timing;
                var navigation = window.performance.getEntriesByType('navigation')[0];
                
                return {
                    dns_time: timing.domainLookupEnd - timing.domainLookupStart,
                    tcp_time: timing.connectEnd - timing.connectStart,
                    request_time: timing.responseStart - timing.requestStart,
                    response_time: timing.responseEnd - timing.responseStart,
                    dom_processing: timing.domComplete - timing.domLoading,
                    dom_interactive: timing.domInteractive - timing.navigationStart,
                    dom_content_loaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    load_complete: timing.loadEventEnd - timing.navigationStart,
                    transfer_size: navigation ? navigation.transferSize : 0,
                    encoded_size: navigation ? navigation.encodedBodySize : 0,
                    decoded_size: navigation ? navigation.decodedBodySize : 0
                };
            """)
            
            # Contar recursos cargados
            resources = driver.execute_script("""
                var resources = window.performance.getEntriesByType('resource');
                var types = {};
                var totalSize = 0;
                
                resources.forEach(function(resource) {
                    var type = resource.initiatorType || 'other';
                    types[type] = (types[type] || 0) + 1;
                    totalSize += resource.transferSize || 0;
                });
                
                return {
                    total: resources.length,
                    by_type: types,
                    total_size: totalSize
                };
            """)
            
            # Obtener información de la página
            page_info = driver.execute_script("""
                return {
                    title: document.title,
                    url: window.location.href,
                    dom_nodes: document.getElementsByTagName('*').length
                };
            """)
            
            logger.info(f"✅ Análisis completado: {page_load_time}ms")
            
            return {
                'timing': {
                    'page_load_ms': page_load_time,
                    'dns_lookup_ms': navigation_timing['dns_time'],
                    'tcp_connection_ms': navigation_timing['tcp_time'],
                    'request_ms': navigation_timing['request_time'],
                    'response_ms': navigation_timing['response_time'],
                    'dom_processing_ms': navigation_timing['dom_processing'],
                    'dom_interactive_ms': navigation_timing['dom_interactive'],
                    'dom_content_loaded_ms': navigation_timing['dom_content_loaded'],
                    'load_complete_ms': navigation_timing['load_complete']
                },
                'resources': {
                    'total_count': resources['total'],
                    'by_type': resources['by_type'],
                    'total_size_bytes': resources['total_size'],
                    'total_size_kb': round(resources['total_size'] / 1024, 2)
                },
                'transfer': {
                    'transfer_size_bytes': navigation_timing['transfer_size'],
                    'encoded_size_bytes': navigation_timing['encoded_size'],
                    'decoded_size_bytes': navigation_timing['decoded_size'],
                    'transfer_size_kb': round(navigation_timing['transfer_size'] / 1024, 2)
                },
                'page': {
                    'title': page_info['title'],
                    'final_url': page_info['url'],
                    'dom_nodes': page_info['dom_nodes']
                },
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        
        except Exception as e:
            logger.error(f"❌ Error analizando rendimiento: {e}")
            raise
        
        finally:
            if driver:
                driver.quit()
    
    def get_lighthouse_metrics(self, url: str) -> Dict:
        """
        Obtener métricas tipo Lighthouse (simuladas)
        
        Args:
            url: URL a analizar
            
        Returns:
            Métricas de rendimiento
        """
        # Nota: Para métricas reales de Lighthouse necesitarías usar
        # lighthouse-cli o puppeteer. Aquí simulamos algunas métricas.
        
        metrics = self.analyze(url)
        
        # Calcular scores básicos (0-100)
        load_time = metrics['timing']['page_load_ms']
        
        # Score simple basado en tiempo de carga
        if load_time < 1000:
            performance_score = 100
        elif load_time < 2500:
            performance_score = 90 - int((load_time - 1000) / 150)
        elif load_time < 5000:
            performance_score = 50 - int((load_time - 2500) / 250)
        else:
            performance_score = max(0, 40 - int((load_time - 5000) / 500))
        
        return {
            'scores': {
                'performance': performance_score,
                'load_time_rating': 'good' if load_time < 2500 else 'needs_improvement' if load_time < 5000 else 'poor'
            },
            'metrics': metrics,
            'recommendations': self._generate_recommendations(metrics)
        }
    
    def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """Generar recomendaciones de optimización"""
        recommendations = []
        
        # Análisis de tiempo de carga
        if metrics['timing']['page_load_ms'] > 3000:
            recommendations.append("Tiempo de carga elevado. Considera optimizar recursos.")
        
        # Análisis de tamaño
        if metrics['transfer']['transfer_size_kb'] > 2000:
            recommendations.append("Tamaño de página grande. Considera comprimir recursos.")
        
        # Análisis de recursos
        resource_count = metrics['resources']['total_count']
        if resource_count > 100:
            recommendations.append(f"Alto número de recursos ({resource_count}). Considera combinar archivos.")
        
        # Análisis de DOM
        if metrics['page']['dom_nodes'] > 1500:
            recommendations.append("DOM muy grande. Puede afectar el rendimiento.")
        
        return recommendations