from multiprocessing import Process, Queue
import time

def productor(q):
    for i in range(10):
        q.put(f'mensaje {i}')
    q.put(None)  # Señal de terminación para el procesador

def procesador(q1, q2):
    while True:
        msg = q1.get()
        if msg is None:
            # Enviar señales de terminación a los consumidores
            for _ in range(2):  # 2 consumidores => 2 mensajes de terminación
                q2.put(None)
            break
        print(f'[PROCESADOR]: Procesando mensaje {msg}')
        time.sleep(1)
        q2.put(msg)  # Enviar mensaje procesado a los consumidores

def consumidor(q, id):
    while True:
        msg = q.get()
        if msg is None:  # Señal de terminación
            print(f'[CONSUMIDOR {id}]: Terminando.')
            break
        print(f'[CONSUMIDOR {id}]: {msg} recibido')

def main():
    q1 = Queue()  # Cola entre productor y procesador
    q2 = Queue()  # Cola entre procesador y consumidores

    p1 = Process(target=productor, args=(q1,))
    p2 = Process(target=procesador, args=(q1, q2))
    p3 = [Process(target=consumidor, args=(q2, i)) for i in range(2)]  # Consumidores leen de q2

    p1.start()
    p2.start()
    for c in p3:
        c.start()

    p1.join()
    p2.join()
    for c in p3:
        c.join()

if __name__ == '__main__':
    main()