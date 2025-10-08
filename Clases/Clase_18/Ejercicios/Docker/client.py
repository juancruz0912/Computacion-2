import socket

HOST = "server"   # nombre del servicio en docker-compose
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.sendto(b"now", (HOST, PORT))          # envío al servidor
    data, addr = s.recvfrom(1024)           # recibo respuesta
    print(f"[CLIENT] Respuesta desde {addr}: {data.decode('utf-8')}")
