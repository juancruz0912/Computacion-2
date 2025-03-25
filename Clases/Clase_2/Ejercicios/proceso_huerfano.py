import os
import time

pid = os.fork()

if pid > 0:
    print(f"Soy el proceso padre (PID: {os.getpid()}), terminando antes que mi hijo.")
else:
    time.sleep(3)  # Espera para que el padre termine antes
    print(f"Soy el proceso huérfano (PID: {os.getpid()}), mi nuevo padre es {os.getppid()}")
