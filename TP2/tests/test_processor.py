import socket
import json
import struct
import argparse


class Protocol:
    """Protocolo para comunicación con el servidor de procesamiento"""
    
    @staticmethod
    def encode_message(data):
        """Codifica un mensaje"""
        json_data = json.dumps(data).encode('utf-8')
        length = len(json_data)
        header = struct.pack('>I', length)
        return header + json_data
    
    @staticmethod
    def decode_message(sock):
        """Decodifica un mensaje"""
        header = sock.recv(4)
        if not header:
            return None
        
        length = struct.unpack('>I', header)[0]
        
        chunks = []
        bytes_received = 0
        
        while bytes_received < length:
            chunk = sock.recv(min(length - bytes_received, 4096))
            if not chunk:
                raise RuntimeError("Socket connection broken")
            chunks.append(chunk)
            bytes_received += len(chunk)
        
        json_data = b''.join(chunks)
        return json.loads(json_data.decode('utf-8'))


def test_task(host, port, task_type, url):
    """
    Enviar una tarea al servidor de procesamiento
    
    Args:
        host: IP del servidor
        port: Puerto del servidor
        task_type: Tipo de tarea ('screenshot', 'performance', 'images', 'all')
        url: URL a procesar
    """
    print(f"🔌 Conectando a {host}:{port}")
    
    # Crear socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        print(f"✅ Conectado\n")
        
        # Preparar request
        request = {
            'task_type': task_type,
            'url': url,
            'timestamp': '2024-11-11T00:00:00Z'
        }
        
        print(f"📤 Enviando request:")
        print(json.dumps(request, indent=2))
        print()
        
        # Enviar request
        message = Protocol.encode_message(request)
        sock.sendall(message)
        
        print(f"⏳ Esperando respuesta...")
        
        # Recibir respuesta
        response = Protocol.decode_message(sock)
        
        print(f"\n📥 Respuesta recibida:")
        print(json.dumps(response, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Cliente de prueba para servidor de procesamiento')
    
    parser.add_argument('-H', '--host', default='localhost', help='Host del servidor')
    parser.add_argument('-p', '--port', type=int, default=9000, help='Puerto del servidor')
    parser.add_argument('-t', '--task', 
                        choices=['screenshot', 'performance', 'images', 'all'],
                        default='all',
                        help='Tipo de tarea a ejecutar')
    parser.add_argument('-u', '--url', default='https://example.com', help='URL a procesar')
    
    args = parser.parse_args()
    
    try:
        test_task(args.host, args.port, args.task, args.url)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()