from multiprocessing import Process, Pipe, Queue
import time
import random
from datetime import datetime
import numpy as np
import hashlib
import json
from queue import Empty

N = 60  # Total de muestras
BLOCKCHAIN_FILE = 'blockchain.json'

# ─────────────────────────────
# Función generadora de datos
# ─────────────────────────────
def generate_sample():
    return {
        "timestamp": datetime.now().isoformat(timespec='seconds'),
        "frecuencia": random.randint(60, 180),
        "presion": [random.randint(110, 180), random.randint(70, 110)], #presion sistólica/diastólica
        "oxigeno": random.randint(90, 100)
    }

# ─────────────────────────────
# Analizador de señales
# ─────────────────────────────
def analyze_sample(tipe, child_pipe, queue):
    window = []

    while True:
        data = child_pipe.recv()
        if data is None:
            break

        # Extraer el valor correspondiente
        if tipe == "frecuencia":
            valor = data["frecuencia"]
        elif tipe == "presion":
            valor = data["presion"][0] # analizamos la presion sistólica, la primera
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
    prev_hash = "0" * 64

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

        # TAREA 2: Verificación de rangos y alertas
        alerta = False
        
        # Verificar frecuencia < 200
        if r1["media"] >= 200:
            alerta = True
            print(f"ALERTA: Frecuencia fuera de rango ({r1['media']} >= 200)")
        
        # Verificar 90 <= oxigeno <= 100
        if not (90 <= r3["media"] <= 100):
            alerta = True
            print(f"ALERTA: Oxígeno fuera de rango ({r3['media']} no está entre 90-100)")
        
        # Verificar presión sistólica < 200
        if r2["media"] >= 200:
            alerta = True
            print(f"ALERTA: Presión sistólica fuera de rango ({r2['media']} >= 200)")

        # Calcular hash del bloque
        hash_bloque = hash_creator(prev_hash, datos, timestamp)
        
        bloque = {
            "timestamp": timestamp,
            "datos": datos,
            "alerta": alerta,
            "prev_hash": prev_hash,
            "hash": hash_bloque
        }

        blockchain.append(bloque)
        prev_hash = hash_bloque  # El hash actual se convierte en el prev_hash del siguiente

        # Mostrar información del bloque
        alerta_text = "🚨 CON ALERTA" if alerta else "✅ Normal"
        print(f"[Bloque #{i+1}] Hash: {bloque['hash'][:16]}... {alerta_text}")

        # Persistir al archivo después de cada bloque
        with open(BLOCKCHAIN_FILE, 'w') as f:
            json.dump(blockchain, f, indent=2)

    print(f"\nBlockchain completado con {len(blockchain)} bloques")
    print(f"Guardado en {BLOCKCHAIN_FILE}")

# ─────────────────────────────
# Proceso principal
# ─────────────────────────────
if __name__ == '__main__':

    parent_pipes = []
    child_pipes = []

    for _ in range(3):
        child_recv, parent_send = Pipe(duplex=False) # duplex = False es un pipe unidireccional
        parent_pipes.append(parent_send)   # principal envía
        child_pipes.append(child_recv)     # analizador recibe

    # Queues: Analizadores -> Verificador
    queue_frecuencia = Queue()
    queue_presion = Queue()
    queue_oxigeno = Queue()

    # Lanzar procesos de análisis
    procesos_analisis = [
       Process(target=analyze_sample, args=("frecuencia", child_pipes[0], queue_frecuencia)),
       Process(target=analyze_sample, args=("presion", child_pipes[1], queue_presion)),
       Process(target=analyze_sample, args=("oxigeno", child_pipes[2], queue_oxigeno))
    ]
    for p in procesos_analisis:
        p.start()

    # Lanzar verificador
    verificator = Process(target=verificate_process, args=(queue_frecuencia, queue_presion, queue_oxigeno))
    verificator.start()

    print("Generando 60 muestras (1 por segundo)...\n")

    # Enviar 60 muestras (1 por segundo)
    for i in range(N):
        sample = generate_sample()
        print(f"Muestra {i+1}/{N}: F={sample['frecuencia']}, P={sample['presion']}, O={sample['oxigeno']}")
        
        for pipe in parent_pipes:
            pipe.send(sample) # se le envia la muestra a los analizadores
        time.sleep(1) # esperar un segundo por muestra

    # Señal de terminación
    for pipe in parent_pipes:
        pipe.send(None)

    for p in procesos_analisis:
        p.join()

    queue_frecuencia.put(None)
    queue_presion.put(None)
    queue_oxigeno.put(None)

    verificator.join()
    
    print("\nProcesamiento completado!")