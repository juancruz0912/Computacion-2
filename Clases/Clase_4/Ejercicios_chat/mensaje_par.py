import os
import random

#Objetivo: Implementar una comunicación simple donde el padre envía un número y el hijo responde si es par o impar.

def par_impar(numero):
    if numero % 2 == 0:
        return "El número es par."
    else:
        return "El número es impar."
    
def main():
    r, w = os.pipe()

    pid = os.fork()

    if pid == 0:
        os.close(w)
        mensaje = os.read(r, 1024).decode()
        print(f"Mensaje recibido por el hijo: {mensaje}")
        print(par_impar(int(mensaje)))
        os.close(r)
    
    else:
        os.close(r)
        numero = random.randint(1, 100)
        os.write(w, str(numero).encode())
        os.close(w)


if __name__ == "__main__":
    main()
