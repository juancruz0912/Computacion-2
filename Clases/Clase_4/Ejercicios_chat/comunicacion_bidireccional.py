import os

#Objetivo: Hacer una conversación ida y vuelta entre padre e hijo.

def main():

    padre_a_hijo_r, padre_a_hijo_w = os.pipe()
    hijo_a_padre_r, hijo_a_padre_w = os.pipe()

    pid = os.fork()

    if pid == 0:  # Proceso hijo
        os.close(hijo_a_padre_r)  # Cierra el extremo de lectura del hijo a padre
        os.close(padre_a_hijo_w)  # Cierra el extremo de escritura del padre a hijo

        # Recibe mensaje del padre
        mensaje = os.read(padre_a_hijo_r, 1024).decode()
        print("[HIJO] Hijo recibió:", mensaje)

        # Envía respuesta al padre
        respuesta = "Hola padre, estoy bien. ¿Tú cómo estás?"
        os.write(hijo_a_padre_w, respuesta.encode())

        # Recibe respuesta del padre
        mensaje = os.read(padre_a_hijo_r, 1024).decode()
        print("[HIJO] Hijo recibió:", mensaje)

        os.close(padre_a_hijo_r)  # Cierra el extremo de lectura del padre a hijo
        os.close(hijo_a_padre_w)  # Cierra el extremo de escritura del hijo a padre
        os._exit(0)

    else:  # Proceso padre
        os.close(padre_a_hijo_r)  # Cierra el extremo de lectura del padre a hijo
        os.close(hijo_a_padre_w)  # Cierra el extremo de escritura del hijo a padre

        # Envía mensaje al hijo
        mensaje = "Hola hijo, ¿cómo estás?"
        os.write(padre_a_hijo_w, mensaje.encode())

        # Recibe respuesta del hijo
        respuesta = os.read(hijo_a_padre_r, 1024).decode()
        print("[PADRE] Padre recibió:", respuesta)

        # Envía respuesta al hijo
        mensaje = "Estoy bien, gracias por preguntar."
        os.write(padre_a_hijo_w, mensaje.encode())

        os.close(padre_a_hijo_w)  # Cierra el extremo de escritura del padre a hijo
        os.close(hijo_a_padre_r)  # Cierra el extremo de lectura del hijo a padre
        os.wait()  # Espera a que el proceso hijo termine

if __name__ == "__main__":
    main()
