import os


pid = os.fork()

if pid == 0:
    print(f"Soy el proceso hijo (PID: {os.getpid()}) y el PID de mi padre es {os.getppid()}.")
else:
    print(f"Soy el proceso padre (PID: {os.getpid()}), el PID de mi hijo es {pid}.")
