# Rlock con fibonacci

from multiprocessing import Process ,RLock
import os

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def calcular_fibonacci(lock, id, n):
    with lock:
        resultado = fibonacci(n)
        print(f"Proceso {id}: Fibonacci({n}) = {resultado}")

if __name__ == '__main__':
    
    lock = RLock()
    
    Procesos = [Process(target=calcular_fibonacci, args=(lock, i, i)) for i in range(5)]

    for p in Procesos: p.start()
    for p in Procesos: p.join()
    
