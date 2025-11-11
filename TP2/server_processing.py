import socketserver
import multiprocessing as mp
from multiprocessing import Pool
import argparse
import logging
import time
from datetime import datetime

# Importar el protocolo unificado
from common.protocol import Protocol, MessageType, TaskType

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
    Simula la generación de un screenshot (versión simplificada)
    En la versión completa usaremos Selenium/Playwright
    
    Args:
        data: dict con 'url' y otros parámetros
        
    Returns:
        dict con resultado simulado
    """
    url = data.get('url', '')
    logger.info(f"[Proceso {mp.current_process().name}] Generando screenshot de {url}")
    
    # Simular trabajo pesado
    time.sleep(1)
    
    return {
        'screenshot': 'base64_encoded_screenshot_placeholder',
        'screenshot_size': 1024,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }


def process_performance_task(data):
    """
    Simula el análisis de rendimiento
    
    Args:
        data: dict con 'url' y otros parámetros
        
    Returns:
        dict con métricas de rendimiento simuladas
    """
    url = data.get('url', '')
    logger.info(f"[Proceso {mp.current_process().name}] Analizando rendimiento de {url}")
    
    # Simular trabajo pesado
    time.sleep(0.5)
    
    return {
        'load_time_ms': 1250,
        'total_size_kb': 2048,
        'num_requests': 45,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }


def process_images_task(data):
    """
    Simula el procesamiento de imágenes
    
    Args:
        data: dict con 'url' y lista de imágenes
        
    Returns:
        dict con thumbnails simulados
    """
    url = data.get('url', '')
    logger.info(f"[Proceso {mp.current_process().name}] Procesando imágenes de {url}")
    
    # Simular trabajo pesado
    time.sleep(0.8)
    
    return {
        'thumbnails': [
            'base64_thumb1_placeholder',
            'base64_thumb2_placeholder'
        ],
        'processed_count': 2,
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
            
            # Recibir mensaje del cliente (Servidor A) usando el protocolo unificado
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
            error_response = Protocol.create_error(
                message=str(e)
            )
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
                result = pool.apply(process_screenshot_task, (request_data,))
            
            elif task_type == TaskType.PERFORMANCE.value:
                result = pool.apply(process_performance_task, (request_data,))
            
            elif task_type == TaskType.IMAGES.value:
                result = pool.apply(process_images_task, (request_data,))
            
            elif task_type == TaskType.ALL.value:
                # Procesar todas las tareas en paralelo
                logger.info(f"🔄 Procesando TODAS las tareas para {url}")
                
                screenshot_future = pool.apply_async(process_screenshot_task, (request_data,))
                performance_future = pool.apply_async(process_performance_task, (request_data,))
                images_future = pool.apply_async(process_images_task, (request_data,))
                
                # Esperar resultados con timeout
                result = {
                    'screenshot': screenshot_future.get(timeout=30),
                    'performance': performance_future.get(timeout=30),
                    'images': images_future.get(timeout=30)
                }
            
            else:
                raise ValueError(f"Tipo de tarea desconocido: {task_type}")
            
            # Crear respuesta usando el protocolo
            return Protocol.create_response(
                task_type=task_type,
                result=result
            )
        
        except Exception as e:
            logger.error(f"❌ Error procesando tarea {task_type}: {e}")
            
            # Crear mensaje de error usando el protocolo
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
    
    # Permitir reutilizar la dirección inmediatamente
    allow_reuse_address = True
    
    def __init__(self, server_address, num_processes=None):
        """
        Inicializar el servidor
        
        Args:
            server_address: tupla (host, port)
            num_processes: número de procesos en el pool (None = CPU count)
        """
        super().__init__(server_address, ProcessingRequestHandler)
        
        # Crear pool de procesos
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
        description='Servidor de Procesamiento Distribuido',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--ip',
        required=True,
        help='Dirección de escucha'
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
    
    # Crear y configurar el servidor
    server_address = (args.ip, args.port)
    server = ProcessingServer(server_address, num_processes=args.processes)
    
    logger.info(f"🚀 Servidor de Procesamiento iniciado en {args.ip}:{args.port}")
    logger.info(f"⚙️  Procesos en el pool: {server.num_processes}")
    logger.info(f"💡 Presiona Ctrl+C para detener")
    
    try:
        # Iniciar el servidor (bloqueante)
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Deteniendo servidor...")
    finally:
        server.shutdown()
        logger.info("👋 Servidor detenido")


if __name__ == '__main__':
    main()