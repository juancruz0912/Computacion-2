# Escribe un programa donde 5 procesos intentan escribir mensajes en un único archivo de log (log.txt). 
# Cada mensaje debe incluir el ID del proceso y una marca de tiempo. Usa un Lock para asegurar que las líneas de log 
# no se mezclen y cada escritura sea completa.

from multiprocessing import Process ,Lock
import datetime
import os

def escribir_log(lock, id, archivo_log):
    with lock:
        with open(archivo_log, 'a') as f:
            f.write(f"Proceso {id}: {datetime.datetime.now()}\n")
        print(f"Proceso {id}: Escrito en {archivo_log}")
    


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