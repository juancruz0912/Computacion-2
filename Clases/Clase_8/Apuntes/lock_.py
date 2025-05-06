from multiprocessing import Process, Lock

#def sumar(lock, nombre):  Forma antigua de hacerlo, con lock.acquire() y lock.release()
#    lock.acquire()
#    print(f"{nombre} accediendo al recurso")
#    # Sección crítica
#    for _ in range(3):
#        print(f"{nombre} trabajando...")
#    lock.release()

def sumar(lock, nombre): # Forma moderna de hacerlo, con with lock, donde cuando termina el bloque, libera el lock
    with lock:
        print(f"{nombre} accediendo al recurso")
        for _ in range(3):
            print(f"{nombre} trabajando...")


if __name__ == '__main__':
    lock = Lock()
    p1 = Process(target=sumar, args=(lock, "Proceso 1"))
    p2 = Process(target=sumar, args=(lock, "Proceso 2"))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Procesos terminados.")