import os

def bidireccional():
    # Creamos dos pipes
    padre_a_hijo_r, padre_a_hijo_w = os.pipe()
    hijo_a_padre_r, hijo_a_padre_w = os.pipe()

    pid = os.fork()

    if pid == 0:
        # Hijo
        os.close(hijo_a_padre_r)

        mensaje = os.read(padre_a_hijo_r, 1024).decode()
        print("Hijo recibió:", mensaje)
        os.close(padre_a_hijo_r)

        respuesta = "Recibido, padre."
        os.write(hijo_a_padre_w, respuesta.encode())
        os.close(hijo_a_padre_w)

    else:
        # Padre
        os.close(padre_a_hijo_r) 
        os.close(hijo_a_padre_w)
        
        mensaje = "Hola hijo, ¿me escuchás?"
        os.write(padre_a_hijo_w,mensaje.encode())
        os.close(padre_a_hijo_w)
        # Esperar respuesta del hijo
        os.wait()
        # Leer respuesta del hijo
        respuesta = os.read(hijo_a_padre_r, 1024).decode()
        print("Padre recibió:", respuesta)

        os.close(hijo_a_padre_r)

if __name__ == "__main__":
    bidireccional()
