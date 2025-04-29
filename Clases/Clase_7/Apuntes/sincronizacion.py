import os
import signal
import time

def handler_usr1(signum, frame):
    print(f"📨 Señal SIGUSR1 recibida por el hijo 2 (PID: {os.getpid()})")

def handler_usr2(signum, frame):
    print(f"📨 Señal SIGUSR2 recibida por el padre (PID: {os.getpid()})")

# Instalar manejadores en todos
signal.signal(signal.SIGUSR1, handler_usr1)
signal.signal(signal.SIGUSR2, handler_usr2)

# Padre crea hijo 1
pid1 = os.fork()

if pid1 == 0:
    # Hijo 1
    time.sleep(2)
    print(f"👶 Hijo 1 (PID: {os.getpid()}): enviando señal a hijo 2...")
    # Leer PID del hijo 2 desde archivo temporal
    with open("pid_hijo2.txt") as f:
        pid_h2 = int(f.read())
    os.kill(pid_h2, signal.SIGUSR1)
    os._exit(0)

else:
    # Padre crea hijo 2
    pid2 = os.fork()
    if pid2 == 0:
        # Hijo 2
        print(f"👶 Hijo 2 (PID: {os.getpid()}) esperando señal de hijo 1...")
        with open("pid_hijo2.txt", "w") as f:
            f.write(str(os.getpid())) # EScribir el pid del hijo 2 en un archivo temporal para que el hijo 1 pueda enviar la señal 
        signal.pause()
        print("👶 Hijo 2 recibió la señal, avisando al padre...")
        os.kill(os.getppid(), signal.SIGUSR2)
        os._exit(0)
    else:
        print(f"🧓 Padre esperando señal final de hijo 2...")
        signal.pause()
        print("✅ Padre reanudado: hijo 2 completó su parte.")

