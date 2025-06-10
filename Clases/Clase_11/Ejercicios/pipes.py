import os

if __name__ == "__main__":
    
    r, w = os.pipe()
    pid = os.fork()

    if pid == 0:
        os.close(r)
        mensaje = f'Hola padre {os.getppid()}, soy tu hijo {os.getpid()}'
        os.write(w, mensaje.encode())
        os.close(w)
        os._exit(0)
    
    else:
        os.close(w)
        mensaje = os.read(r, 1024)
        print("Mensaje recibido por el padre:", mensaje.decode())
        os.close(r)
        os.wait()
