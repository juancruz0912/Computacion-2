from multiprocessing import Process, Queue
import time
import random

def productor(q):
    for i in range(10):
        mensaje = f"Tarea {i}"
        q.put(mensaje)
        print(f"[Productor] Enviado: {mensaje}")
        time.sleep(random.uniform(0.1, 0.4))

    for _ in range(3):  # 3 consumidores => 3 mensajes de terminación
        q.put("terminar")

def consumidor(q, id):
    while True:
        tarea = q.get()
        if tarea == "terminar":
            print(f"[Consumidor {id}] Fin.")
            break
        print(f"[Consumidor {id}] Ejecutando: {tarea}")
        time.sleep(random.uniform(0.5, 1.2))

if __name__ == '__main__':
    q = Queue()
    productores = [Process(target=productor, args=(q,))]
    consumidores = [Process(target=consumidor, args=(q, i)) for i in range(3)]

    for p in productores + consumidores:
        p.start()
    for p in productores + consumidores:
        p.join()

    print("[Main] Proceso terminado.")
