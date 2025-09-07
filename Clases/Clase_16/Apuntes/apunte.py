# telnet localhost 5000

import socket

sp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sp.bind(("0.0.0.0", 5000))
sp.listen(5) # hasta aca es socket pasivo

sa = sp.accept() # aca es un socket activo
print(sa)

sb = sp.accept() # otro socket activo
sc = sp.accept() # otro socket activo

leido_p = sp.recv(100) 
leido_a = sa[0].recv(100)
