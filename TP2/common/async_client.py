"""
Cliente asíncrono para comunicarse con el Servidor de Procesamiento
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from .protocol import Protocol, TaskType

logger = logging.getLogger(__name__)


class ProcessingClient:
    """Cliente asíncrono para comunicarse con el Servidor B"""
    
    def __init__(self, host: str, port: int, timeout: int = 30):
        """
        Inicializar el cliente
        
        Args:
            host: Host del servidor de procesamiento
            port: Puerto del servidor de procesamiento
            timeout: Timeout en segundos para las operaciones
        """
        self.host = host
        self.port = port
        self.timeout = timeout
    
    async def send_task(self, task_type: str, url: str, **params) -> Dict[str, Any]:
        """
        Enviar una tarea al servidor de procesamiento
        
        Args:
            task_type: Tipo de tarea (TaskType)
            url: URL a procesar
            **params: Parámetros adicionales
            
        Returns:
            dict con el resultado del procesamiento
            
        Raises:
            ConnectionError: Si no se puede conectar al servidor
            TimeoutError: Si la operación excede el timeout
            ValueError: Si la respuesta es inválida
        """
        try:
            # Crear la solicitud
            request = Protocol.create_request(task_type, url, **params)
            
            logger.info(f"Conectando al servidor de procesamiento {self.host}:{self.port}")
            
            # Conectar al servidor de forma asíncrona
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=5  # Timeout de conexión de 5 segundos
            )
            
            try:
                logger.info(f"Enviando tarea tipo '{task_type}' para URL: {url}")
                
                # Codificar y enviar el mensaje
                message_bytes = Protocol.encode_message(request)
                writer.write(message_bytes)
                await writer.drain()
                
                logger.debug(f"Mensaje enviado ({len(message_bytes)} bytes)")
                
                # Recibir la respuesta con timeout
                response = await asyncio.wait_for(
                    self._receive_response(reader),
                    timeout=self.timeout
                )
                
                logger.info(f"Respuesta recibida: {response.get('status', 'unknown')}")
                
                return response
            
            finally:
                # Cerrar la conexión
                writer.close()
                await writer.wait_closed()
                logger.debug("Conexión cerrada")
        
        except asyncio.TimeoutError:
            logger.error(f"Timeout comunicándose con {self.host}:{self.port}")
            raise TimeoutError(f"Timeout después de {self.timeout}s")
        
        except ConnectionRefusedError:
            logger.error(f"Conexión rechazada por {self.host}:{self.port}")
            raise ConnectionError(f"Servidor de procesamiento no disponible en {self.host}:{self.port}")
        
        except Exception as e:
            logger.error(f"Error comunicándose con servidor de procesamiento: {e}")
            raise
    
    async def _receive_response(self, reader: asyncio.StreamReader) -> Dict[str, Any]:
        """
        Recibir y decodificar la respuesta del servidor
        
        Args:
            reader: StreamReader de asyncio
            
        Returns:
            dict con la respuesta decodificada
        """
        # Leer el header (4 bytes)
        header = await reader.readexactly(Protocol.HEADER_SIZE)
        
        if not header:
            raise ValueError("Respuesta vacía del servidor")
        
        # Decodificar longitud
        import struct
        (length,) = struct.unpack(Protocol.HEADER_FORMAT, header)
        
        # Verificar tamaño
        if length > Protocol.MAX_MESSAGE_SIZE:
            raise ValueError(f"Respuesta demasiado grande: {length} bytes")
        
        # Leer el payload completo
        payload = await reader.readexactly(length)
        
        # Decodificar JSON
        import json
        response = json.loads(payload.decode('utf-8'))
        
        # Validar la respuesta
        Protocol.validate_message(response)
        
        return response
    
    async def request_screenshot(self, url: str) -> Dict[str, Any]:
        """Solicitar generación de screenshot"""
        return await self.send_task(TaskType.SCREENSHOT.value, url)
    
    async def request_performance(self, url: str) -> Dict[str, Any]:
        """Solicitar análisis de rendimiento"""
        return await self.send_task(TaskType.PERFORMANCE.value, url)
    
    async def request_images(self, url: str) -> Dict[str, Any]:
        """Solicitar procesamiento de imágenes"""
        return await self.send_task(TaskType.IMAGES.value, url)
    
    async def request_all(self, url: str) -> Dict[str, Any]:
        """Solicitar todas las tareas en paralelo"""
        return await self.send_task(TaskType.ALL.value, url)