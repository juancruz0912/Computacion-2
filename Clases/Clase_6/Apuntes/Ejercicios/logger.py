import os

fifo = 'canal_fifo'
logfile = 'registro.log'

with open(fifo, 'r') as f, open(logfile, 'a') as log:
    print("[Logger] Esperando mensajes...")
    while True:
        mensaje = f.readline()
        if mensaje == '':
            break  # EOF si se cierra el canal
        print("[Logger] Registrando:", mensaje.strip())
        log.write(mensaje)
