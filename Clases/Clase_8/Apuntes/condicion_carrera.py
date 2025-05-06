from multiprocessing import Process, Value

def incrementar(contador):
    for _ in range(1000):
        contador.value += 1  # Esto puede causar errores si se ejecuta simultáneamente

if __name__ == '__main__':
    contador = Value('i', 0)
    p1 = Process(target=incrementar, args=(contador,))
    p2 = Process(target=incrementar, args=(contador,))

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print("Valor final:", contador.value)
