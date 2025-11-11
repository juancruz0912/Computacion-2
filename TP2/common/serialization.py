"""
Utilidades de serialización para diferentes tipos de datos
"""

import json
import pickle
import base64
import logging
from typing import Any, Dict
from enum import Enum

logger = logging.getLogger(__name__)


class SerializationFormat(Enum):
    """Formatos de serialización soportados"""
    JSON = "json"
    PICKLE = "pickle"
    MSGPACK = "msgpack"  # Para implementar en el futuro


class Serializer:
    """Clase para serializar/deserializar datos"""
    
    @staticmethod
    def serialize_json(data: Any) -> str:
        """
        Serializar datos a JSON
        
        Args:
            data: Datos a serializar
            
        Returns:
            String JSON
        """
        try:
            return json.dumps(data, ensure_ascii=False, indent=None)
        except (TypeError, ValueError) as e:
            logger.error(f"Error serializando a JSON: {e}")
            raise
    
    @staticmethod
    def deserialize_json(json_str: str) -> Any:
        """
        Deserializar desde JSON
        
        Args:
            json_str: String JSON
            
        Returns:
            Datos deserializados
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Error deserializando JSON: {e}")
            raise
    
    @staticmethod
    def serialize_pickle(data: Any) -> bytes:
        """
        Serializar datos con pickle (para objetos Python complejos)
        
        Args:
            data: Datos a serializar
            
        Returns:
            bytes serializados
        """
        try:
            return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        except pickle.PicklingError as e:
            logger.error(f"Error serializando con pickle: {e}")
            raise
    
    @staticmethod
    def deserialize_pickle(data: bytes) -> Any:
        """
        Deserializar desde pickle
        
        Args:
            data: bytes serializados
            
        Returns:
            Datos deserializados
        """
        try:
            return pickle.loads(data)
        except pickle.UnpicklingError as e:
            logger.error(f"Error deserializando pickle: {e}")
            raise
    
    @staticmethod
    def encode_base64(data: bytes) -> str:
        """
        Codificar bytes en base64 (útil para imágenes, screenshots, etc.)
        
        Args:
            data: bytes a codificar
            
        Returns:
            String base64
        """
        return base64.b64encode(data).decode('ascii')
    
    @staticmethod
    def decode_base64(b64_str: str) -> bytes:
        """
        Decodificar desde base64
        
        Args:
            b64_str: String base64
            
        Returns:
            bytes decodificados
        """
        return base64.b64decode(b64_str.encode('ascii'))
    
    @staticmethod
    def prepare_for_json(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preparar datos para serialización JSON
        Convierte bytes a base64, etc.
        
        Args:
            data: Diccionario con datos
            
        Returns:
            Diccionario serializable en JSON
        """
        result = {}
        
        for key, value in data.items():
            if isinstance(value, bytes):
                # Convertir bytes a base64
                result[key] = {
                    '_type': 'base64',
                    'data': Serializer.encode_base64(value)
                }
            elif isinstance(value, dict):
                # Recursivo para diccionarios anidados
                result[key] = Serializer.prepare_for_json(value)
            elif isinstance(value, list):
                # Procesar listas
                result[key] = [
                    Serializer.prepare_for_json({'item': item})['item']
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def restore_from_json(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restaurar datos desde JSON
        Convierte base64 a bytes, etc.
        
        Args:
            data: Diccionario deserializado
            
        Returns:
            Diccionario con tipos restaurados
        """
        result = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                # Verificar si es un objeto especial
                if value.get('_type') == 'base64':
                    result[key] = Serializer.decode_base64(value['data'])
                else:
                    # Recursivo para diccionarios anidados
                    result[key] = Serializer.restore_from_json(value)
            elif isinstance(value, list):
                # Procesar listas
                result[key] = [
                    Serializer.restore_from_json({'item': item})['item']
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result