"""
Protocolo de comunicación entre servidores

Formato del mensaje:
[4 bytes: longitud][N bytes: mensaje JSON]

Tipos de mensajes:
- REQUEST: Cliente solicita procesamiento
- RESPONSE: Servidor envía resultado
- ERROR: Ocurrió un error
"""

import struct
import json
import logging
from enum import Enum
from typing import Dict, Any, Optional, Union, BinaryIO
from datetime import datetime
import socket

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Tipos de mensajes soportados"""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


class TaskType(Enum):
    """Tipos de tareas que puede procesar el Servidor B"""
    SCREENSHOT = "screenshot"
    PERFORMANCE = "performance"
    IMAGES = "images"
    ALL = "all"  # Ejecutar todas las tareas en paralelo


class Protocol:
    """
    Protocolo de comunicación para mensajes entre servidores
    
    Formato del mensaje:
    - Header: 4 bytes (entero big-endian) indicando longitud del payload
    - Payload: JSON UTF-8 con la estructura del mensaje
    """
    
    # Constantes
    HEADER_SIZE = 4
    MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10 MB
    HEADER_FORMAT = '>I'  # Unsigned int, big-endian
    
    @staticmethod
    def create_request(task_type: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Crear un mensaje de solicitud
        
        Args:
            task_type: Tipo de tarea (TaskType)
            url: URL a procesar
            **kwargs: Parámetros adicionales
            
        Returns:
            dict con la estructura del request
        """
        return {
            'message_type': MessageType.REQUEST.value,
            'task_type': task_type,
            'url': url,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'params': kwargs
        }
    
    @staticmethod
    def create_response(task_type: str, result: Any, **kwargs) -> Dict[str, Any]:
        """
        Crear un mensaje de respuesta exitosa
        
        Args:
            task_type: Tipo de tarea procesada
            result: Resultado del procesamiento
            **kwargs: Metadatos adicionales
            
        Returns:
            dict con la estructura del response
        """
        return {
            'message_type': MessageType.RESPONSE.value,
            'status': 'success',
            'task_type': task_type,
            'result': result,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'metadata': kwargs
        }
    
    @staticmethod
    def create_error(message: str, task_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Crear un mensaje de error
        
        Args:
            message: Descripción del error
            task_type: Tipo de tarea que falló (opcional)
            **kwargs: Información adicional del error
            
        Returns:
            dict con la estructura del error
        """
        return {
            'message_type': MessageType.ERROR.value,
            'status': 'error',
            'task_type': task_type,
            'error_message': message,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'details': kwargs
        }
    
    @staticmethod
    def encode_message(data: Dict[str, Any]) -> bytes:
        """
        Codificar un mensaje para enviar por socket
        
        Args:
            data: Diccionario con los datos del mensaje
            
        Returns:
            bytes codificados (header + payload)
            
        Raises:
            ValueError: Si el mensaje es demasiado grande
        """
        try:
            # Serializar a JSON
            json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            # Verificar tamaño
            if len(json_data) > Protocol.MAX_MESSAGE_SIZE:
                raise ValueError(
                    f"Mensaje demasiado grande: {len(json_data)} bytes "
                    f"(máximo: {Protocol.MAX_MESSAGE_SIZE})"
                )
            
            # Crear header con la longitud
            header = struct.pack(Protocol.HEADER_FORMAT, len(json_data))
            
            return header + json_data
        
        except (TypeError, ValueError) as e:
            logger.error(f"Error codificando mensaje: {e}")
            raise
    
    @staticmethod
    def decode_message(sock: Union[socket.socket, BinaryIO]) -> Optional[Dict[str, Any]]:
        """
        Decodificar un mensaje recibido por socket o archivo binario
        
        Args:
            sock: Socket o objeto BinaryIO del cual leer
            
        Returns:
            dict con los datos decodificados o None si no hay datos
            
        Raises:
            RuntimeError: Si la conexión se cierra inesperadamente
            ValueError: Si el mensaje está corrupto o es demasiado grande
        """
        try:
            # Leer header (4 bytes)
            header = Protocol._recv_exact(sock, Protocol.HEADER_SIZE)
            
            if not header:
                return None
            
            # Desempaquetar longitud
            (length,) = struct.unpack(Protocol.HEADER_FORMAT, header)
            
            # Verificar tamaño razonable
            if length > Protocol.MAX_MESSAGE_SIZE:
                raise ValueError(
                    f"Mensaje demasiado grande: {length} bytes "
                    f"(máximo: {Protocol.MAX_MESSAGE_SIZE})"
                )
            
            # Leer el payload completo
            json_data = Protocol._recv_exact(sock, length)
            
            if not json_data:
                raise RuntimeError("Conexión cerrada mientras se leía el payload")
            
            # Decodificar JSON
            return json.loads(json_data.decode('utf-8'))
        
        except (struct.error, json.JSONDecodeError) as e:
            logger.error(f"Error decodificando mensaje: {e}")
            raise ValueError(f"Mensaje corrupto: {e}")
    
    @staticmethod
    def _recv_exact(sock: Union[socket.socket, BinaryIO], num_bytes: int) -> bytes:
        """
        Recibir exactamente num_bytes del socket o archivo
        
        Args:
            sock: Socket o BinaryIO del cual leer
            num_bytes: Número exacto de bytes a leer
            
        Returns:
            bytes leídos
            
        Raises:
            RuntimeError: Si la conexión se cierra antes de leer todos los bytes
        """
        chunks = []
        bytes_received = 0
        
        while bytes_received < num_bytes:
            # Determinar cuántos bytes leer en este chunk
            bytes_to_read = min(num_bytes - bytes_received, 4096)
            
            # Leer según el tipo de objeto
            if hasattr(sock, 'recv'):
                # Es un socket real
                chunk = sock.recv(bytes_to_read)
            elif hasattr(sock, 'read'):
                # Es un objeto tipo archivo (BytesIO, FileIO, etc.)
                chunk = sock.read(bytes_to_read)
            else:
                raise TypeError(f"Objeto no soportado: {type(sock)}")
            
            if not chunk:
                if bytes_received == 0:
                    return b''  # Conexión cerrada limpiamente
                else:
                    raise RuntimeError(
                        f"Conexión cerrada después de {bytes_received}/{num_bytes} bytes"
                    )
            
            chunks.append(chunk)
            bytes_received += len(chunk)
        
        return b''.join(chunks)
    
    @staticmethod
    def validate_message(data: Dict[str, Any]) -> bool:
        """
        Validar que un mensaje tenga la estructura correcta
        
        Args:
            data: Diccionario con el mensaje
            
        Returns:
            True si es válido
            
        Raises:
            ValueError: Si el mensaje es inválido
        """
        # Validar que tenga el campo message_type
        if 'message_type' not in data:
            raise ValueError("Mensaje sin campo 'message_type'")
        
        msg_type = data['message_type']
        
        # Validar según el tipo de mensaje
        if msg_type == MessageType.REQUEST.value:
            required_fields = ['task_type', 'url']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"REQUEST sin campo '{field}'")
        
        elif msg_type == MessageType.RESPONSE.value:
            required_fields = ['status', 'task_type', 'result']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"RESPONSE sin campo '{field}'")
        
        elif msg_type == MessageType.ERROR.value:
            if 'error_message' not in data:
                raise ValueError("ERROR sin campo 'error_message'")
        
        else:
            raise ValueError(f"Tipo de mensaje desconocido: {msg_type}")
        
        return True