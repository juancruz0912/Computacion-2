'''
Cree un script que instale un manejador para la señal SIGUSR1. El proceso deberá estar en espera pasiva (pause() o bucle infinito).

Desde Bash, envíe la señal al proceso con kill -SIGUSR1 [pid] y verifique la respuesta.
'''

import signal
import os

def manejar_salida(signum, frame):
    
    print("\n Proceso terminado por el usuario")
    exit(1)  # Terminamos el programa

if __name__ == "__main__":
    print(f'Iniciando programa, mi pid es {os.getpid()}')
    while True:
        signal.signal(signal.SIGUSR1, manejar_salida)


'''
Respuestas:

-> % python3 Señales.py
Iniciando programa, mi pid es 15913

 Proceso terminado por el usuario

-> % kill -SIGUSR1 15913

'''