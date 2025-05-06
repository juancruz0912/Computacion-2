from multiprocessing import Process
import os, time

def tarea(w):
    print(f"Proceso con PID {os.getpid()} iniciado")
    os.write(w, b"Hola desde el proceso hijo")
    os.close(w)

if __name__ == '__main__':
    r, w = os.pipe()
    p1 = Process(target=tarea, args=(w,))
    p1.start()
    os.close(w)  # El padre cierra el extremo de escritura

    print("Proceso iniciado, esperando que termine...")
    mensaje = os.read(r, 1024)
    print("Mensaje recibido por el padre:", mensaje.decode())
    print(os.getpid())
    time.sleep(30)
    os.close(r)
    p1.join()
    print("El proceso hijo ha terminado.")