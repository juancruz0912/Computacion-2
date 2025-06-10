'''
Utilice multiprocessing.Process para crear 4 procesos que escriban 
su identificador y una marca de tiempo en un mismo archivo de log. 
Utilice multiprocessing.Lock para evitar colisiones.
'''
import os
from multiprocessing import Process, Lock

def escribir_log(lock, i, archivo_log):
    with lock:
        print(f'[PROCESO {i}]: Escribiendo mensaje...\n')
        mensaje = f'Proceso {i} presente\n'
        with open(archivo_log, "a") as f:
            f.write(mensaje)



if __name__ == '__main__':

    lock = Lock()

    archivo_log = 'log.txt'
    if os.path.exists(archivo_log): os.remove(archivo_log) # Limpia el log anterior

    Procesos = [Process(target=escribir_log, args=(lock, i, archivo_log)) for i in range(5)]

    for p in Procesos: p.start()
    for p in Procesos: p.join()
    
    print(f"\nContenido de {archivo_log}:\n---")
    with open(archivo_log, 'r') as f: print(f.read())
    print("---")
    

