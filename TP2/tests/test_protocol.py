"""
Tests para validar el protocolo de comunicación
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Ahora sí podemos importar
from common.protocol import Protocol, MessageType, TaskType
import json


def test_encode_decode():
    """Probar codificación y decodificación básica"""
    print("🧪 Test 1: Encode/Decode básico")
    
    # Crear un mensaje de request
    request = Protocol.create_request(
        task_type=TaskType.SCREENSHOT.value,
        url="https://example.com"
    )
    
    print(f"Request original:")
    print(json.dumps(request, indent=2))
    
    # Codificar
    encoded = Protocol.encode_message(request)
    print(f"\n✅ Codificado: {len(encoded)} bytes")
    
    # Simular socket con el mensaje
    import io
    fake_socket = io.BytesIO(encoded)
    
    # Decodificar
    decoded = Protocol.decode_message(fake_socket)
    print(f"\nRequest decodificado:")
    print(json.dumps(decoded, indent=2))
    
    # Validar
    assert decoded == request
    print("\n✅ Test 1 PASSED\n")


def test_validate_messages():
    """Probar validación de mensajes"""
    print("🧪 Test 2: Validación de mensajes")
    
    # Mensaje válido
    valid_request = Protocol.create_request(
        task_type=TaskType.ALL.value,
        url="https://python.org"
    )
    
    try:
        Protocol.validate_message(valid_request)
        print("✅ Mensaje REQUEST válido")
    except ValueError as e:
        print(f"❌ Error: {e}")
    
    # Mensaje inválido (sin URL)
    invalid_request = {
        'message_type': MessageType.REQUEST.value,
        'task_type': TaskType.SCREENSHOT.value
        # Falta 'url'
    }
    
    try:
        Protocol.validate_message(invalid_request)
        print("❌ Debería haber fallado la validación")
    except ValueError as e:
        print(f"✅ Error esperado capturado: {e}")
    
    print("\n✅ Test 2 PASSED\n")


def test_response_messages():
    """Probar mensajes de respuesta"""
    print("🧪 Test 3: Mensajes de respuesta y error")
    
    # Respuesta exitosa
    response = Protocol.create_response(
        task_type=TaskType.PERFORMANCE.value,
        result={
            'load_time_ms': 1250,
            'total_size_kb': 2048
        }
    )
    
    print("Response creado:")
    print(json.dumps(response, indent=2))
    
    # Mensaje de error
    error = Protocol.create_error(
        message="URL no accesible",
        task_type=TaskType.SCREENSHOT.value,
        status_code=404
    )
    
    print("\nError creado:")
    print(json.dumps(error, indent=2))
    
    print("\n✅ Test 3 PASSED\n")


if __name__ == '__main__':
    print("="*60)
    print("TESTS DEL PROTOCOLO DE COMUNICACIÓN")
    print("="*60 + "\n")
    
    test_encode_decode()
    test_validate_messages()
    test_response_messages()
    
    print("="*60)
    print("✅ TODOS LOS TESTS PASARON")
    print("="*60)