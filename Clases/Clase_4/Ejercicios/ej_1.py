# Crea un programa en Python que establezca comunicación entre un proceso padre y un hijo mediante un pipe. 
# El padre debe enviar un mensaje al hijo, y el hijo debe recibir ese mensaje y devolverlo al padre (eco).

import os 

def main():
    r1, w1 = os.pipe()  # Pipe para que el padre se comunique con el hijo
    r2, w2 = os.pipe()  # Pipe para que el hijo se comunique con el padre

    pid = os.fork()  # Creamos el hijo

    if pid == 0:  # Proceso hijo
        os.close(w1)  # Cerramos el extremo de escritura del primer pipe
        os.close(r2)  # Cerramos el extremo de lectura del segundo pipe

        # Leer mensaje del padre
        mensaje = os.read(r1, 1024)
        print('[HIJO] Recibí el mensaje:', mensaje.decode())

        # Enviar respuesta al padre
        respuesta = 'Hola padre, mensaje recibido'
        os.write(w2, respuesta.encode())

        # Cerrar los extremos restantes
        os.close(r1)
        os.close(w2)
        os._exit(0)  # Salimos del hijo

    else:  # Proceso padre
        os.close(r1)  # Cerramos el extremo de lectura del primer pipe
        os.close(w2)  # Cerramos el extremo de escritura del segundo pipe

        # Enviar mensaje al hijo
        mensaje = 'Hola hijo, ¿me escuchás?'
        os.write(w1, mensaje.encode())

        # Esperar al hijo
        os.wait()

        # Leer respuesta del hijo
        respuesta = os.read(r2, 1024)
        print('[PADRE] Recibí el mensaje:', respuesta.decode())

        # Cerrar los extremos restantes
        os.close(r2)
        os.close(w1)

if __name__ == "__main__":
    main()