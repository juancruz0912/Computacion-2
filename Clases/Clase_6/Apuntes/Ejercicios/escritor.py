import os
import time

fifo = 'canal_fifo'

with open(fifo, 'w') as f:
    for i in range(3):
        mensaje = f"Mensaje {i}\n"
        print("Enviando:", mensaje.strip())
        f.write(mensaje)
        f.flush()
        time.sleep(1)  # Tiempo para permitir que los lectores lean
