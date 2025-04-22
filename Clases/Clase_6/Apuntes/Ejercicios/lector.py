import os

fifo = 'canal_fifo'

with open(fifo, 'r') as f:
    print("[Lector 1] Leyendo:")
    print(f.read())
