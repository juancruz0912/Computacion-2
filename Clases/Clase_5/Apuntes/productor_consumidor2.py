from multiprocessing import Process, Queue
import time
import random


#  Dos productores generan tareas, dos consumidores las procesan. 
# Coordinación completa.
def productor(q, id):
    for i in range(10):
        mensaje = f"Tarea {i}"
        q.put(mensaje)
        print(f"[Productor {id}] Enviado: {mensaje}")
        time.sleep(random.uniform(0.1, 0.4))


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
    productores = [Process(target=productor, args=(q, i,)) for i in range(2)]
    consumidores = [Process(target=consumidor, args=(q, i)) for i in range(2)]

    for p in productores: p.start()
    for p in productores: p.join()

    # Cuando todos los productores terminaron, mandás señales de fin:
    for _ in consumidores:
        q.put("terminar")

    for c in consumidores: c.start()
    for c in consumidores: c.join()

    print("[Main] Proceso terminado.")
