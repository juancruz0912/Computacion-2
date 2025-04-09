# Objetivo: Simular un pipeline como echo "hola" | rev | tr 'a-z' 'A-Z'.

import os

def main():
    r1, w1 = os.pipe()
    r2, w2 = os.pipe()

    pid = os.fork()

    if pid == 0:  # Proceso hijo
        os.close(w1)
        os.close(r2)
        os.dup2(r1, 0) # Redirige el stdin de la terminal al pipe de lectura
        os.dup2(w2, 1) # Redirige el stdout de la terminar del pipe de escritura para que la lo escrito en la terminal se escriba en el pipe
        os.close(r1)
        os.close(w2)
        os.execlp("rev", "rev")    
    else:  # Proceso padre
        pid2 = os.fork()

        if pid2 == 0:  # Proceso hijo2
            os.close(w1)
            os.close(r1)
            os.close(w2)
            os.dup2(r2, 0) # lee lo  escrito en la terminal gracias al dup2(w2,1) que se hizo anteriormente
            os.execlp("tr", "tr", "a-z", "A-Z") # Ejecuta el comando tr y lo muestra en la terminal
            os.close(r2)
        
        else:
            os.close(r1)
            os.close(r2)
            os.close(w2)
            mensaje = "Hola"
            os.write(w1, mensaje.encode())
            os.close(w1)
            os.wait()

if __name__ == '__main__':
    main()


