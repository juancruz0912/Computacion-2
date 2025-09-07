# Enviar a broadcast para descubrir servicios en la red local.
# nc -u -l -p 9006 para UDP

import socket

PORT = 9008
BROADCAST = ("255.255.255.255", PORT)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # habilita el broadcast
    s.settimeout(5.0)
    s.sendto(b"DISCOVER?", BROADCAST)
    try:
        data, addr = s.recvfrom(4096)
        print(f"{addr} -> {data!r}")
    except socket.timeout:
        print("Nadie respondió al broadcast (o la red lo filtra)")