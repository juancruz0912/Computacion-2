import os

pid = os.fork()

if pid > 0:
    # Proceso padre
    print(f"Soy el proceso padre, esperando al hijo...")
    os.wait()  # Espera a que el proceso hijo termine
    print("El proceso hijo ha terminado.")
else:
    # Proceso hijo
    print(f"Soy el proceso hijo, ejecutando tarea...")
