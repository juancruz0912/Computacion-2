import os

def main():
    # Crear pipe: devuelve (lectura, escritura)
    r, w = os.pipe()

    # Crear proceso hijo
    pid = os.fork()

    if pid > 0:
        # Estamos en el proceso PADRE
        os.close(r)  # Cerrar extremo de lectura

        mensaje = "Hola hijo, soy tu padre.\n"
        os.write(w, mensaje.encode())
          # Cerrar después de escribir
        os.wait()    # Esperar al hijo

    else:
        # Estamos en el proceso HIJO
        os.close(w)  # Cerrar extremo de escritura

        # Leer datos del padre
        mensaje = os.read(r, 1024)
        print("Mensaje recibido por el hijo:", mensaje.decode())
        os.close(r)

if __name__ == "__main__":
    main()
