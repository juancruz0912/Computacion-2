import socket
import os
import signal

# Función para limpiar procesos zombis
def reap_zombie_processes(signum, frame):
    while True:
        try:
            pid, _ = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break
        except ChildProcessError:
            break

# Asigna el manejador de la señal SIGCHLD
signal.signal(signal.SIGCHLD, reap_zombie_processes)

# Creación del socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 9999))
server_socket.listen(5)

print("Servidor esperando conexiones en el puerto 9999...")

while True:
    client_socket, addr = server_socket.accept()
    print(f"Conexión recibida de {addr}")

    pid = os.fork()
    
    if pid == 0:  # Proceso hijo
        server_socket.close()  # El hijo no necesita el socket del servidor
        client_socket.sendall(b"Hola, cliente! Bienvenido al servidor.\n")
        client_socket.close()
        os._exit(0)  # Termina el proceso hijo
    else:  # Proceso padre
        client_socket.close()  # El padre cierra el socket del cliente
