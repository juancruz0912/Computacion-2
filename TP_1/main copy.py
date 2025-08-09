import os
import time
import random
from datetime import datetime
import numpy as np
import hashlib
import json
import queue
N = 60  # Total de muestras
BLOCKCHAIN_FILE = 'blockchain.json'

# ─────────────────────────────
# Función generadora de datos
# ─────────────────────────────
def generate_sample():
    return {
        "timestamp": datetime.now().isoformat(timespec='seconds'),
        "frecuencia": random.randint(60, 180),
        "presion": [random.randint(110, 180), random.randint(70, 110)],
        "oxigeno": random.randint(90, 100)
    }

# ─────────────────────────────
# Analizador de señales
# ─────────────────────────────
def analyze_sample(tipe, child_pipe, queue):
    window = []

    while True:
        data = os.read(child_pipe, 1024)  # Leer del pipe
        data = data.decode()
        if data is None:
            break

        # Extraer el valor correspondiente
        if tipe == "frecuencia":
            valor = data["frecuencia"]
        elif tipe == "presion":
            valor = data["presion"][0]
        elif tipe == "oxigeno":
            valor = data["oxigeno"]
        else:
            continue

        window.append(valor)
        if len(window) > 30:
            window = window[-30:] # solo los ultimos 30 valores

        if len(window) >= 2:
            valores_np = np.array(window, dtype=np.float64)
            media = np.mean(valores_np)
            desv = np.std(valores_np, ddof=1)
        else: # para el primer valor que llega
            media = float(valor)
            desv = 0.0

        resultado = {
            "tipo": tipe,
            "timestamp": data["timestamp"],
            "media": round(media, 2),
            "desv": round(desv, 2)
        }

        queue.put(resultado)

# ─────────────────────────────
# Función hash para bloques
# ─────────────────────────────
def hash_creator(prev_hash, datos, timestamp):
    datos_str = json.dumps(datos, sort_keys=True, separators=(',', ':'))
    content = f"{prev_hash}{datos_str}{timestamp}".encode()
    return hashlib.sha256(content).hexdigest()
# ─────────────────────────────
# Verificador de resultados
# ─────────────────────────────
def verificate_process(qf, qp, qo):
    blockchain = []

    for i in range(N):
        try: # obtener los valores de las colas
            r1 = qf.get(timeout=2)
            r2 = qp.get(timeout=2)
            r3 = qo.get(timeout=2)
        except Empty:
            print("⚠️ Timeout esperando resultados")
            break

        if any(r is None for r in [r1, r2, r3]):
            break

        timestamp = r1["timestamp"]
        datos = {
            "frecuencia": {"media": r1["media"], "desv": r1["desv"]},
            "presion": {"media": r2["media"], "desv": r2["desv"]},
            "oxigeno": {"media": r3["media"], "desv": r3["desv"]}
        }

        if i == 0: 
            prev_hash = "0" * 64 #primer bloque
        else:
            prev_hash = blockchain[-1]['hash']
        bloque = {
            "timestamp": timestamp,
            "datos": datos,
            "alerta": False,  # Tarea 2 se encargará de validar
            "prev_hash": prev_hash,
            "hash": hash_creator(prev_hash, datos, timestamp)
        }

        blockchain.append(bloque)

        print(f"[Bloque #{len(blockchain)}] Hash: {bloque['hash']}")

        with open(BLOCKCHAIN_FILE, 'w') as f:
            json.dump(blockchain, f, indent=2)

# ─────────────────────────────
# Proceso principal
# ─────────────────────────────
if __name__ == '__main__':

    # Crear pipes para comunicación
    pipe_fds = []
    for _ in range(3):
        read_fd, write_fd = os.pipe()
        pipe_fds.append((read_fd, write_fd))

    # Queues: Analizadores -> Verificador
    queue_frecuencia = queue.Queue()
    queue_presion = queue.Queue()
    queue_oxigeno = queue.Queue()

    # Crear procesos de análisis usando fork
    child_pids = []
    for i, (read_fd, write_fd) in enumerate(pipe_fds):
        pid = os.fork()
        if pid == 0:  # Proceso hijo
            os.close(write_fd)  # Cerrar el descriptor de escritura en el hijo
            if i == 0:
                analyze_sample("frecuencia", read_fd, queue_frecuencia)
            elif i == 1:
                analyze_sample("presion", read_fd, queue_presion)
            else:
                analyze_sample("oxigeno", read_fd, queue_oxigeno)
            os._exit(0)
        else:  # Proceso padre
            os.close(read_fd)  # Cerrar el descriptor de lectura en el padre
            child_pids.append(pid)

    # Crear proceso verificador usando fork
    pid = os.fork()
    if pid == 0:  # Proceso hijo (verificador)
        verificate_process(queue_frecuencia, queue_presion, queue_oxigeno)
        os._exit(0)
    else:  # Proceso padre
        verificator_pid = pid

    # Enviar 60 muestras (1 por segundo)
    for _ in range(N):
        sample = generate_sample()
        for pipe in pipe_fds:
            os.write(write_fd, json.dumps(sample).encode())
        time.sleep(1) # esperar un segundo por muestra

    # Señal de terminación
    for pipe in pipe_fds:
        os.write(pipe[1], json.dumps(None).encode())

    for p in child_pids:
        os.waitpid(p, 0)

    os.waitpid(verificator_pid, 0)
