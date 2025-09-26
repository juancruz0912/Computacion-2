import socket

HOST = "server"   # nombre del servicio en docker-compose
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"now")
    data = s.recv(1024)

print(f"[CLIENT] Respuesta del servidor: {data.decode('utf-8')}")
