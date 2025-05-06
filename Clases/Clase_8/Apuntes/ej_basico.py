from multiprocessing import Process
import time, os

def tarea(nombre):
    print(f"Proceso {nombre} con PID {os.getpid()} iniciado")
    time.sleep(2)
    print(f"Proceso {nombre} con PID {os.getpid()} finalizado")

if __name__ == '__main__':
    p1 = Process(target=tarea, args=("Uno",))
    p2 = Process(target=tarea, args=("Dos",))

    p1.start()
    p2.start()


    print("Procesos iniciados, esperando que terminen...")

    p1.join()
    p2.join()

    print("Ambos procesos han terminado.")
