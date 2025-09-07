# nc -l -p 9006 -s 127.0.0.1 para TCP
# nc -u -l -p 9006 -s 127.0.0.1 para UDP


import socket

HOST, PORT = "127.0.0.1", 9006

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  
    s.sendto(b"ping", (HOST, PORT)) # manda datos
    data, addr = s.recvfrom(2048) # recibe el dato
    print(f"< {data!r} desde {addr}") # mumestra el dato

    # En el ultimo corri el servidor y mande pong, el  #En otra terminal, estoy compartiendo sol
    