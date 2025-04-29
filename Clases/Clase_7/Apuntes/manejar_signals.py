import signal
import os
import time

def manejar_sigterm(signum, frame):
    print("📴 Señal SIGINT recibida. Terminando...")
    exit(0)

signal.signal(signal.SIGINT, manejar_sigterm)

pid = os.fork()

if pid == 0:
    print(f"Soy el proceso hijo (PID: {os.getpid()}) y el PID de mi padre es {os.getppid()}.")
    time.sleep(3)
    os.kill(os.getppid(), signal.SIGINT)
else:
    print(f"Soy el proceso padre (PID: {os.getpid()}), el PID de mi hijo es {pid}.")
    signal.pause()
print("✅ Fin del programa")
