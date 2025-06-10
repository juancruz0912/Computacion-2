'''

Ejercicio 9: Control de concurrencia con Semaphore
Implemente una versión del problema de los "puestos limitados" usando multiprocessing.Semaphore. 
Cree 10 procesos que intenten acceder a una zona crítica que solo permite 3 accesos simultáneos.

'''

from multiprocessing import Process, Semaphore, current_process
import time
import random

def funcion(semaforo):

    semaforo.acquire()
    print(f"Proceso {current_process().name}: Accediendo a la zona crítica")
    time.sleep(random.randint(1, 5))
    semaforo.release()
    print(f"Proceso {current_process().name}: Sale de la zona crítica")



if __name__ == '__main__':

    n = 3 #cantidad de accesos permitidos
    semaforo = Semaphore(n)
    
    Procesos = [Process(target=funcion, args=(semaforo,)) for _ in range(10)]

    for p in Procesos: p.start()
    for p in Procesos: p.join()

    