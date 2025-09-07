import socket
import time

HOST, PORT = "127.0.0.1", 9007

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.settimeout(4.0)
    retries = 3
    for i in range(1, retries + 1):
        try:
            s.sendto(b"TIME", (HOST, PORT))
            time.sleep(3)
            data, _ = s.recvfrom(2048) # si no recibe la info, salta al bloque except
            print("Respuesta:", data.decode()) #envia un time esperando respuesta
            break
        except socket.timeout:
            print(f"Timeout intento {i}; reintentando...")
    else:
        print("Sin respuesta tras reintentos")