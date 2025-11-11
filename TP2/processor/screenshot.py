import logging
import base64
import io
from typing import Dict, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PIL import Image

logger = logging.getLogger(__name__)


class ScreenshotGenerator:
    """Generador de screenshots usando Selenium"""
    
    def __init__(self, headless: bool = True, width: int = 1920, height: int = 1080):
        """
        Inicializar el generador
        
        Args:
            headless: Ejecutar en modo headless (sin GUI)
            width: Ancho de la ventana del navegador
            height: Alto de la ventana del navegador
        """
        self.headless = headless
        self.width = width
        self.height = height
    
    def _create_driver(self) -> webdriver.Chrome:
        """
        Crear una instancia del WebDriver de Chrome
        
        Returns:
            WebDriver configurado
        """
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # Opciones para mejorar rendimiento y estabilidad
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(f'--window-size={self.width},{self.height}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
        
        # Desactivar imágenes para acelerar carga (opcional)
        # chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        return driver
    
    def capture(self, url: str, wait_time: int = 3) -> Dict:
        """
        Capturar screenshot de una URL
        
        Args:
            url: URL a capturar
            wait_time: Tiempo de espera para que cargue la página (segundos)
            
        Returns:
            Diccionario con el screenshot y metadatos
        """
        driver = None
        
        try:
            logger.info(f"📸 Capturando screenshot de {url}")
            
            # Crear driver
            driver = self._create_driver()
            
            # Navegar a la URL
            start_time = datetime.utcnow()
            driver.get(url)
            
            # Esperar a que la página cargue
            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            load_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Capturar screenshot
            screenshot_png = driver.get_screenshot_as_png()
            
            # Convertir a base64
            screenshot_b64 = base64.b64encode(screenshot_png).decode('ascii')
            
            # Obtener dimensiones de la imagen
            img = Image.open(io.BytesIO(screenshot_png))
            width, height = img.size
            
            logger.info(f"✅ Screenshot capturado: {width}x{height} ({len(screenshot_png)} bytes)")
            
            return {
                'screenshot_base64': screenshot_b64,
                'format': 'png',
                'size_bytes': len(screenshot_png),
                'dimensions': {
                    'width': width,
                    'height': height
                },
                'load_time_seconds': round(load_time, 2),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        
        except Exception as e:
            logger.error(f"❌ Error capturando screenshot de {url}: {e}")
            raise
        
        finally:
            if driver:
                driver.quit()
    
    def capture_full_page(self, url: str) -> Dict:
        """
        Capturar screenshot de página completa (scroll completo)
        
        Args:
            url: URL a capturar
            
        Returns:
            Diccionario con el screenshot
        """
        driver = None
        
        try:
            logger.info(f"📸 Capturando screenshot completo de {url}")
            
            driver = self._create_driver()
            driver.get(url)
            
            # Esperar carga
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Obtener altura total de la página
            total_height = driver.execute_script("return document.body.scrollHeight")
            
            # Ajustar ventana para capturar página completa
            driver.set_window_size(self.width, total_height)
            
            # Capturar
            screenshot_png = driver.get_screenshot_as_png()
            screenshot_b64 = base64.b64encode(screenshot_png).decode('ascii')
            
            img = Image.open(io.BytesIO(screenshot_png))
            width, height = img.size
            
            logger.info(f"✅ Screenshot completo: {width}x{height}")
            
            return {
                'screenshot_base64': screenshot_b64,
                'format': 'png',
                'size_bytes': len(screenshot_png),
                'dimensions': {
                    'width': width,
                    'height': height
                },
                'full_page': True,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            raise
        
        finally:
            if driver:
                driver.quit()
    
    def capture_thumbnail(self, url: str, thumb_width: int = 400) -> Dict:
        """
        Capturar screenshot y generar thumbnail
        
        Args:
            url: URL a capturar
            thumb_width: Ancho del thumbnail
            
        Returns:
            Diccionario con screenshot y thumbnail
        """
        # Capturar screenshot normal
        screenshot_data = self.capture(url)
        
        # Decodificar imagen
        screenshot_png = base64.b64decode(screenshot_data['screenshot_base64'])
        img = Image.open(io.BytesIO(screenshot_png))
        
        # Calcular dimensiones del thumbnail manteniendo aspect ratio
        aspect_ratio = img.height / img.width
        thumb_height = int(thumb_width * aspect_ratio)
        
        # Crear thumbnail
        img.thumbnail((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        
        # Convertir a bytes
        thumb_buffer = io.BytesIO()
        img.save(thumb_buffer, format='PNG')
        thumb_png = thumb_buffer.getvalue()
        thumb_b64 = base64.b64encode(thumb_png).decode('ascii')
        
        logger.info(f"🖼️  Thumbnail generado: {thumb_width}x{thumb_height}")
        
        screenshot_data['thumbnail'] = {
            'thumbnail_base64': thumb_b64,
            'dimensions': {
                'width': thumb_width,
                'height': thumb_height
            },
            'size_bytes': len(thumb_png)
        }
        
        return screenshot_data