"""
Protocolo de comunicación unificado entre servidores
"""
import json
import struct
from enum import Enum
from typing import Dict, Any
import asyncio
import logging

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Tipos de mensajes"""
    REQUEST = 'request'
    RESPONSE = 'response'
    ERROR = 'error'


class TaskType(Enum):
    """Tipos de tareas de procesamiento"""
    SCREENSHOT = 'screenshot'
    PERFORMANCE = 'performance'
    IMAGES = 'images'
    TECHNOLOGIES = 'technologies'  # ✅ NUEVO
    SEO = 'seo'                     # ✅ NUEVO
    ALL = 'all'


class Protocol:
    """
    Protocolo de comunicación basado en JSON con prefijo de longitud
    
    Formato del mensaje:
    [4 bytes: longitud][JSON data]
    """
    
    @staticmethod
    def create_request(task_type: TaskType, url: str, params: dict = None) -> dict:
        """
        Crear un mensaje de request
        
        Args:
            task_type: Tipo de tarea (TaskType enum)
            url: URL a procesar
            params: Parámetros adicionales (opcional)
        
        Returns:
            dict con el mensaje de request
        """
        return {
            'type': MessageType.REQUEST.value,
            'task_type': task_type.value if isinstance(task_type, TaskType) else task_type,
            'url': url,
            'params': params or {}
        }
    
    @staticmethod
    def create_response(task_type: str, result: Dict[str, Any]) -> dict:
        """
        Crear un mensaje de response
        
        Args:
            task_type: Tipo de tarea procesada
            result: Resultado del procesamiento
        
        Returns:
            dict con el mensaje de response
        """
        return {
            'type': MessageType.RESPONSE.value,
            'task_type': task_type,
            'result': result
        }
    
    @staticmethod
    def create_error(message: str, task_type: str = None) -> dict:
        """
        Crear un mensaje de error
        
        Args:
            message: Mensaje de error
            task_type: Tipo de tarea que causó el error (opcional)
        
        Returns:
            dict con el mensaje de error
        """
        error_msg = {
            'type': MessageType.ERROR.value,
            'error': message
        }
        
        if task_type:
            error_msg['task_type'] = task_type
        
        return error_msg
    
    @staticmethod
    def encode_message(message: dict) -> bytes:
        """
        Codificar mensaje a bytes con prefijo de longitud
        
        Args:
            message: Diccionario con el mensaje
        
        Returns:
            bytes con [longitud de 4 bytes][JSON]
        """
        json_data = json.dumps(message, ensure_ascii=False)
        json_bytes = json_data.encode('utf-8')
        
        # Crear prefijo de longitud (4 bytes, big-endian)
        length_prefix = struct.pack('>I', len(json_bytes))
        
        return length_prefix + json_bytes
    
    @staticmethod
    def decode_message(sock) -> dict:
        """
        Decodificar mensaje desde socket
        
        Args:
            sock: Socket del que leer
        
        Returns:
            dict con el mensaje decodificado
        """
        try:
            # Leer prefijo de longitud (4 bytes)
            length_data = sock.recv(4)
            
            if not length_data or len(length_data) < 4:
                return None
            
            # Decodificar longitud
            message_length = struct.unpack('>I', length_data)[0]
            
            # Leer el mensaje completo
            chunks = []
            bytes_received = 0
            
            while bytes_received < message_length:
                chunk = sock.recv(min(message_length - bytes_received, 8192))
                
                if not chunk:
                    break
                
                chunks.append(chunk)
                bytes_received += len(chunk)
            
            # Combinar chunks y decodificar JSON
            json_data = b''.join(chunks).decode('utf-8')
            return json.loads(json_data)
        
        except Exception as e:
            logger.error(f"Error decodificando mensaje: {e}")
            return None
    
    @staticmethod
    async def receive_message(reader: asyncio.StreamReader) -> dict:
        """
        Recibir mensaje de forma asíncrona
        
        Args:
            reader: StreamReader de asyncio
        
        Returns:
            dict con el mensaje decodificado
        """
        try:
            # Leer prefijo de longitud (4 bytes)
            length_data = await reader.readexactly(4)
            
            if not length_data:
                return None
            
            # Decodificar longitud
            message_length = struct.unpack('>I', length_data)[0]
            
            # Leer el mensaje completo
            json_bytes = await reader.readexactly(message_length)
            
            # Decodificar JSON
            json_data = json_bytes.decode('utf-8')
            return json.loads(json_data)
        
        except asyncio.IncompleteReadError:
            logger.warning("Conexión cerrada antes de recibir mensaje completo")
            return None
        
        except Exception as e:
            logger.error(f"Error recibiendo mensaje: {e}")
            return None
    
    @staticmethod
    def validate_message(message: dict) -> bool:
        """
        Validar que un mensaje tenga el formato correcto
        
        Args:
            message: Mensaje a validar
        
        Returns:
            True si es válido
        
        Raises:
            ValueError: Si el mensaje es inválido
        """
        if not isinstance(message, dict):
            raise ValueError("Message must be a dictionary")
        
        # Verificar tipo de mensaje
        msg_type = message.get('type')
        if msg_type not in [t.value for t in MessageType]:
            raise ValueError(f"Invalid message type: {msg_type}")
        
        # Validar según tipo
        if msg_type == MessageType.REQUEST.value:
            if 'task_type' not in message:
                raise ValueError("Request message must have 'task_type'")
            
            if 'url' not in message:
                raise ValueError("Request message must have 'url'")
        
        elif msg_type == MessageType.RESPONSE.value:
            if 'result' not in message:
                raise ValueError("Response message must have 'result'")
        
        elif msg_type == MessageType.ERROR.value:
            if 'error' not in message:
                raise ValueError("Error message must have 'error'")
        
        return True