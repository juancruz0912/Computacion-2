from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import random

def tarea(id):
    duracion = random.uniform(1, 3)
    time.sleep(duracion)
    return f"Tarea {id} tardó {duracion:.2f}s"

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(tarea, i) for i in range(5)] #submit manda a ejecutar las tareas
    
    # Procesar según terminan (no en orden)
    for future in as_completed(futures): #ordena los elementos segun el tiempo de finalización
        print(future.result())