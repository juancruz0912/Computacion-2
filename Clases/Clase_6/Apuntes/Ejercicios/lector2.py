import os

fifo = 'canal_fifo'

with open(fifo, 'r') as f:
    print("[Lector 2] Leyendo:")
    print(f.read())
