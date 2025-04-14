#Desarrolla un sistema de chat simple entre dos procesos usando pipes. 
#Cada proceso debe poder enviar y recibir mensajes simultáneamente, implementando una comunicación bidireccional completa.

import os

def recibir_mensaje(r, who):
    mensaje = os.read(r, 1024)
    if mensaje:  # Verificar que el mensaje no esté vacío
        print(f'[{who}] Recibí el mensaje:', mensaje.decode())
        return mensaje.decode() 
    else:
        return None

def enviar_mensaje(w, who):
    mensaje = input(f'[{who}] Enviar mensaje: ')
    os.write(w, mensaje.encode())
    return mensaje  # Devolver el mensaje para que el bucle lo evalúe

def main():

    r1, w1 = os.pipe()
    r2, w2 = os.pipe()
    
    print('Entrando a la charla, cuando quiera finalizar escriba "salir"')

    pid = os.fork()
    
    if pid == 0:  # Proceso hijo
        who = 'HIJO'
        os.close(w1)  # Cerrar extremo de escritura del primer pipe
        os.close(r2)  # Cerrar extremo de lectura del segundo pipe

        while True:
            # Leer mensaje del padre
            mensaje = recibir_mensaje(r1, who)

            
            # Enviar respuesta al padre
            mensaje = enviar_mensaje(w2, who)
            if mensaje == "salir":
                break

        # Cerrar los extremos restantes una vez finalizada la charla
        os.close(r1)
        os.close(w2)
        os._exit(0)  # Salimos del hijo

    else:  # Proceso padre
        who = 'PADRE'
        os.close(w2)  # Cerrar extremo de escritura del segundo pipe
        os.close(r1)  # Cerrar extremo de lectura del primer pipe

        while True:
            # Enviar mensaje al hijo
            mensaje = enviar_mensaje(w1, who)
            if mensaje == "salir":
                break
            
            # Leer mensaje del hijo
            mensaje = recibir_mensaje(r2, who)


        # Cerrar los extremos restantes una vez finalizada la charla
        os.close(r2)
        os.close(w1)
        os._exit(0)  # Salimos del padre    

if __name__ == "__main__":
    main()