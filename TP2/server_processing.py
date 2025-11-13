import socketserver
import multiprocessing as mp
from multiprocessing import Pool
import argparse
import logging
import time
from datetime import datetime

# Importar el protocolo unificado
from common.protocol import Protocol, MessageType, TaskType

# Importar los procesadores reales
from processor.screenshot import ScreenshotGenerator
from processor.performance import PerformanceAnalyzer
from processor.image_processor import ImageProcessor

# ✅ IMPORTAR NUEVOS ANALIZADORES (BONUS TRACK 3)
from processor.technology_detector import TechnologyDetector
from processor.seo_analyzer import SEOAnalyzer

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# FUNCIONES QUE SE EJECUTARÁN EN PROCESOS SEPARADOS
# ============================================================================

def process_screenshot_task(data):
    """
    Generar screenshot usando Selenium/Chromium
    
    Args:
        data: dict con 'url' y otros parámetros
        
    Returns:
        dict con resultado del screenshot
    """
    url = data.get('url', '')
    logger.info(f"[Proceso {mp.current_process().name}] Generando screenshot de {url}")
    
    try:
        generator = ScreenshotGenerator(headless=True)
        result = generator.capture(url)
        
        logger.info(f"[Proceso {mp.current_process().name}] Screenshot completado")
        return result
    
    except Exception as e:
        logger.error(f"[Proceso {mp.current_process().name}] Error: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


def process_performance_task(data):
    """
    Analizar rendimiento usando Selenium
    
    Args:
        data: dict con 'url' y otros parámetros
        
    Returns:
        dict con métricas de rendimiento
    """
    url = data.get('url', '')
    logger.info(f"[Proceso {mp.current_process().name}] Analizando rendimiento de {url}")
    
    try:
        analyzer = PerformanceAnalyzer(headless=True)
        result = analyzer.analyze(url)
        
        logger.info(f"[Proceso {mp.current_process().name}] Análisis completado")
        return result
    
    except Exception as e:
        logger.error(f"[Proceso {mp.current_process().name}] Error: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


def process_images_task(data):
    """
    Procesar imágenes de la página
    
    Args:
        data: dict con 'url' y lista de imágenes
        
    Returns:
        dict con thumbnails procesados
    """
    url = data.get('url', '')
    image_urls = data.get('params', {}).get('image_urls', [])
    
    logger.info(f"[Proceso {mp.current_process().name}] Procesando {len(image_urls)} imágenes de {url}")
    
    try:
        import asyncio
        
        processor = ImageProcessor()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            processor.process_images(image_urls[:10], create_thumbnails=True)
        )
        
        loop.close()
        
        logger.info(f"[Proceso {mp.current_process().name}] Procesamiento completado")
        return result
    
    except Exception as e:
        logger.error(f"[Proceso {mp.current_process().name}] Error: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


# ✅ NUEVA FUNCIÓN: Detectar Tecnologías
def process_technologies_task(data):
    """
    Detectar tecnologías web utilizadas
    
    Args:
        data: dict con 'url', 'html_content' y 'headers'
        
    Returns:
        dict con tecnologías detectadas
    """
    url = data.get('url', '')
    html_content = data.get('params', {}).get('html_content', '')
    headers = data.get('params', {}).get('headers', {})
    
    logger.info(f"[Proceso {mp.current_process().name}] Detectando tecnologías de {url}")
    
    try:
        detector = TechnologyDetector()
        result = detector.analyze(html_content, headers)
        
        logger.info(
            f"[Proceso {mp.current_process().name}] "
            f"Detección completada: {result.get('summary', {}).get('total_technologies', 0)} tecnologías"
        )
        return result
    
    except Exception as e:
        logger.error(f"[Proceso {mp.current_process().name}] Error: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


# ✅ NUEVA FUNCIÓN: Analizar SEO
def process_seo_task(data):
    """
    Analizar SEO de la página
    
    Args:
        data: dict con 'url' y 'html_content'
        
    Returns:
        dict con análisis de SEO
    """
    url = data.get('url', '')
    html_content = data.get('params', {}).get('html_content', '')
    
    logger.info(f"[Proceso {mp.current_process().name}] Analizando SEO de {url}")
    
    try:
        analyzer = SEOAnalyzer()
        result = analyzer.analyze(html_content, url)
        
        logger.info(
            f"[Proceso {mp.current_process().name}] "
            f"Análisis completado: Score {result.get('score', 0)}/100 (Grade: {result.get('grade', 'N/A')})"
        )
        return result
    
    except Exception as e:
        logger.error(f"[Proceso {mp.current_process().name}] Error: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }


# ============================================================================
# HANDLER PARA PROCESAR REQUESTS
# ============================================================================

class ProcessingRequestHandler(socketserver.BaseRequestHandler):
    """Handler que procesa cada request en el servidor"""
    
    def handle(self):
        """Manejar una conexión entrante"""
        try:
            logger.info(f"📨 Nueva conexión desde {self.client_address}")
            
            # Recibir mensaje del cliente usando el protocolo unificado
            request_data = Protocol.decode_message(self.request)
            
            if not request_data:
                logger.warning("⚠️  Mensaje vacío recibido")
                return
            
            # Validar el mensaje
            try:
                Protocol.validate_message(request_data)
            except ValueError as e:
                logger.error(f"❌ Mensaje inválido: {e}")
                error_response = Protocol.create_error(
                    message=f"Invalid message format: {str(e)}"
                )
                self.request.sendall(Protocol.encode_message(error_response))
                return
            
            logger.info(f"📦 Request recibido: {request_data.get('task_type', 'unknown')}")
            
            # Procesar la tarea
            response = self.process_task(request_data)
            
            # Enviar respuesta
            response_bytes = Protocol.encode_message(response)
            self.request.sendall(response_bytes)
            
            logger.info(f"✅ Respuesta enviada a {self.client_address}")
        
        except Exception as e:
            logger.error(f"❌ Error manejando request: {e}")
            error_response = Protocol.create_error(message=str(e))
            try:
                self.request.sendall(Protocol.encode_message(error_response))
            except:
                pass
    
    def process_task(self, request_data):
        """
        Procesar una tarea usando el pool de procesos
        
        Args:
            request_data: dict con la tarea a procesar
            
        Returns:
            dict con el resultado (ya en formato Protocol)
        """
        task_type = request_data.get('task_type', 'unknown')
        url = request_data.get('url', '')
        
        # Obtener el pool de procesos del servidor
        pool = self.server.process_pool
        
        try:
            # Seleccionar la función apropiada según el tipo de tarea
            if task_type == TaskType.SCREENSHOT.value:
                logger.info(f"🎯 Procesando tarea SCREENSHOT para {url}")
                result = pool.apply(process_screenshot_task, (request_data,))
            
            elif task_type == TaskType.PERFORMANCE.value:
                logger.info(f"🎯 Procesando tarea PERFORMANCE para {url}")
                result = pool.apply(process_performance_task, (request_data,))
            
            elif task_type == TaskType.IMAGES.value:
                logger.info(f"🎯 Procesando tarea IMAGES para {url}")
                result = pool.apply(process_images_task, (request_data,))
            
            # ✅ NUEVAS TAREAS (BONUS TRACK 3)
            elif task_type == 'technologies':
                logger.info(f"🎯 Procesando tarea TECHNOLOGIES para {url}")
                result = pool.apply(process_technologies_task, (request_data,))
            
            elif task_type == 'seo':
                logger.info(f"🎯 Procesando tarea SEO para {url}")
                result = pool.apply(process_seo_task, (request_data,))
            
            elif task_type == TaskType.ALL.value:
                # ✅ PROCESAR TODAS LAS TAREAS EN PARALELO (INCLUYENDO NUEVAS)
                logger.info(f"🔄 Procesando TODAS las tareas para {url}")
                
                # Lanzar todas las tareas en paralelo
                screenshot_future = pool.apply_async(process_screenshot_task, (request_data,))
                performance_future = pool.apply_async(process_performance_task, (request_data,))
                images_future = pool.apply_async(process_images_task, (request_data,))
                
                # ✅ AGREGAR NUEVAS TAREAS AL PROCESAMIENTO PARALELO
                technologies_future = pool.apply_async(process_technologies_task, (request_data,))
                seo_future = pool.apply_async(process_seo_task, (request_data,))
                
                # Esperar resultados con timeout de 60 segundos
                try:
                    screenshot_result = screenshot_future.get(timeout=60)
                    performance_result = performance_future.get(timeout=60)
                    images_result = images_future.get(timeout=60)
                    technologies_result = technologies_future.get(timeout=60)
                    seo_result = seo_future.get(timeout=60)
                    
                    result = {
                        'screenshot': screenshot_result,
                        'performance': performance_result,
                        'images': images_result,
                        'technologies': technologies_result,  # ✅ NUEVO
                        'seo': seo_result                      # ✅ NUEVO
                    }
                    
                    logger.info("✅ Todas las tareas completadas (incluyendo análisis avanzados)")
                
                except mp.TimeoutError:
                    logger.error("⏱️  Timeout procesando tareas")
                    raise Exception("Processing timeout (60s exceeded)")
            
            else:
                raise ValueError(f"Tipo de tarea desconocido: {task_type}")
            
            # Crear respuesta usando el protocolo
            return Protocol.create_response(
                task_type=task_type,
                result=result
            )
        
        except Exception as e:
            logger.error(f"❌ Error procesando tarea {task_type}: {e}")
            return Protocol.create_error(
                message=str(e),
                task_type=task_type
            )


# ============================================================================
# SERVIDOR TCP CON POOL DE PROCESOS
# ============================================================================

class ProcessingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Servidor TCP que maneja requests usando threads y procesa tareas con multiprocessing
    """
    
    allow_reuse_address = True
    
    def __init__(self, server_address, num_processes=None):
        """
        Inicializar el servidor
        
        Args:
            server_address: tupla (host, port)
            num_processes: número de procesos en el pool (None = CPU count)
        """
        super().__init__(server_address, ProcessingRequestHandler)
        
        if num_processes is None:
            num_processes = mp.cpu_count()
        
        self.num_processes = num_processes
        self.process_pool = Pool(processes=num_processes)
        
        logger.info(f"🔧 Pool de procesos creado con {num_processes} workers")
    
    def shutdown(self):
        """Cerrar el pool de procesos antes de apagar el servidor"""
        logger.info("🛑 Cerrando pool de procesos...")
        self.process_pool.close()
        self.process_pool.join()
        super().shutdown()


# ============================================================================
# FUNCIONES PRINCIPALES
# ============================================================================

def parse_arguments():
    """Parsear argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Servidor de Procesamiento Distribuido con Análisis Avanzados',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s -i localhost -p 9000
  %(prog)s -i 0.0.0.0 -p 9000 -n 4
  %(prog)s -i :: -p 9000 -n 8

Tareas soportadas:
  - screenshot     : Captura de pantalla
  - performance    : Análisis de rendimiento
  - images         : Procesamiento de imágenes
  - technologies   : Detección de tecnologías web (NUEVO)
  - seo            : Análisis de SEO (NUEVO)
  - all            : Todas las tareas en paralelo
        """
    )
    
    parser.add_argument(
        '-i', '--ip',
        required=True,
        help='Dirección de escucha (IPv4/IPv6)'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        required=True,
        help='Puerto de escucha'
    )
    
    parser.add_argument(
        '-n', '--processes',
        type=int,
        default=None,
        help=f'Número de procesos en el pool (default: {mp.cpu_count()})'
    )
    
    return parser.parse_args()


def main():
    """Función principal"""
    args = parse_arguments()
    
    server_address = (args.ip, args.port)
    server = ProcessingServer(server_address, num_processes=args.processes)
    
    logger.info("=" * 70)
    logger.info("🚀 SERVIDOR DE PROCESAMIENTO INICIADO")
    logger.info("=" * 70)
    logger.info(f"📍 Dirección: {args.ip}:{args.port}")
    logger.info(f"⚙️  Procesos en el pool: {server.num_processes}")
    logger.info(f"🖥️  CPUs disponibles: {mp.cpu_count()}")
    logger.info(f"\n💡 Tareas soportadas:")
    logger.info(f"   - screenshot     : Captura de pantalla (Selenium)")
    logger.info(f"   - performance    : Análisis de rendimiento")
    logger.info(f"   - images         : Procesamiento de imágenes")
    logger.info(f"   - technologies   : Detección de tecnologías web ✨ NUEVO")
    logger.info(f"   - seo            : Análisis de SEO ✨ NUEVO")
    logger.info(f"   - all            : Todas las tareas en paralelo")
    logger.info(f"\n💡 Presiona Ctrl+C para detener")
    logger.info("=" * 70)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Deteniendo servidor...")
    finally:
        server.shutdown()
        logger.info("👋 Servidor detenido correctamente")


if __name__ == '__main__':
    main()