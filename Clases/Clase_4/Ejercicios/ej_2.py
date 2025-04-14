# Implementa un sistema donde el proceso padre lee un archivo de texto y envía su contenido línea por línea 
# a un proceso hijo a través de un pipe. 
# El hijo debe contar las palabras en cada línea y devolver el resultado al padre.

import os

def contar_palabras(linea):
    return len(linea.split())


def main():
    # Crear pipe
    r, w = os.pipe()

    # Crear proceso hijo
    pid = os.fork()

    if pid == 0:
        # Estamos en el proceso hijo
        os.close(w)  # Cerrar extremo de escritura
        mensaje = os.read(r, 1024)  # Leer del pipe
        lineas = mensaje.decode().splitlines()
        for linea in lineas:
            if linea:
                palabras = contar_palabras(linea)
                print(f"[HIJO] La línea '{linea}' tiene {palabras} palabras.")
        os.close(r)
        os._exit(0)


    else:
        # Estamos en el proceso padre
        os.close(r)  # Cerrar extremo de lectura

        # Abrir el archivo
        with open('archivo.txt', 'r') as f:
            for line in f:
                # Enviar línea al hijo
                os.write(w, line.encode())
        os.wait()  # Esperar a que el hijo termine
        os.close(w)


if __name__ == "__main__":
    main()