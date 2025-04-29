import threading
import signal
import time
import os

# Evento para comunicar que se recibió la señal
evento_parar = threading.Event()

# Hilo de trabajo
def hilo_secundario():
    print("🧵 Hilo secundario iniciado")
    while not evento_parar.is_set():
        print("💼 Trabajando en el hilo secundario...")
        time.sleep(1)
    print("🛑 Hilo secundario detenido por la señal")

# Manejador de señal en el hilo principal
def manejador_sigint(signum, frame):
    print(f"📡 Señal {signum} recibida (SIGINT / Ctrl+C)")
    evento_parar.set()

# Asociar la señal en el hilo principal
signal.signal(signal.SIGINT, manejador_sigint)

# Iniciar el hilo
hilo = threading.Thread(target=hilo_secundario)
hilo.start()

print(f"PID del proceso: {os.getpid()}")
print("Presioná Ctrl+C para detener el hilo...")

# Esperar a que termine el hilo
hilo.join()
print("✅ Programa finalizado correctamente")

