import os
import time


def crear_proceso(time_sleep, child):
    pid = os.fork()
    if pid == 0:  # Proceso hijo
        time.sleep(time_sleep)
        print(f"Hijo {child} con PID {os.getpid()} ha terminado. El PID del padre es {os.getppid()}.")
        os._exit(0)  # Termina el proceso hijo
    else:  # Proceso padre
        os.wait()  # Espera a que el hijo termine
        print(f"Proceso padre con PID {os.getpid()} ha terminado.")


if __name__ == "__main__":
    for i in range(5):
        crear_proceso(1, i)