'''
Ejercicio 8: Condición de Carrera y su Corrección

Implemente un contador compartido entre dos procesos sin usar Lock, para evidenciar una condición de carrera. 
Luego modifique el programa para corregir el problema usando multiprocessing.Lock.

Compare ambos resultados.
'''

from multiprocessing import Process, Lock, Value

def contar(lock, contador, id):
    for j in range(100):
        with lock:
            contador.value += 1
            print(f'Proceso con lock {id}: {contador.value}')

def contar_mal(contador, id):
    for j in range(100):
        contador.value += 1
        print(f'Proceso sin lock {id}: {contador.value}')

if __name__ == '__main__':
    lock = Lock()
    
    contador = Value('i', 0)
    contador_mal = Value('i', 0)

    procesos_con_lock = [Process(target=contar, args=(lock, contador, _)) for _ in range(2)]
    procesos_sin_lock = [Process(target=contar_mal, args=(contador_mal, _)) for _ in range(2)]

    for p in procesos_con_lock: p.start()
    for p in procesos_sin_lock: p.start()
    
    for p in procesos_con_lock: p.join()
    for p in procesos_sin_lock: p.join()