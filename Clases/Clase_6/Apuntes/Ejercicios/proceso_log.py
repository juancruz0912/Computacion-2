import os
import sys

fifo = 'canal_fifo'

mensaje = sys.argv[1] if len(sys.argv) > 1 else "Mensaje sin contenido"

with open(fifo, 'w') as f:
    f.write(f"{mensaje}\n")
    print("Mensaje enviado al log.")
