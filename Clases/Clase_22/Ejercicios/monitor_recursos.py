import psutil
import time
import threading
from concurrent.futures import ThreadPoolExecutor


detenerse = threading.Event() #Evento global para detener los hilos correctamente con Ctrl+C

resultados = {
    'cpu': [],
    'memoria': [],
    'disco': []
}

# === Funciones de monitoreo ===
def monitorear_cpu(resultados, intervalo=5):
    while not detenerse.is_set():
        cpu = psutil.cpu_percent(interval=1)
        resultados['cpu'].append(cpu)
        time.sleep(intervalo)

def monitorear_memoria(resultados, intervalo=5):
    while not detenerse.is_set():
        memoria = psutil.virtual_memory().percent
        resultados['memoria'].append(memoria)
        time.sleep(intervalo)

def monitorear_disco(resultados, intervalo=5):
    while not detenerse.is_set():
        disco = psutil.disk_usage('/').percent
        resultados['disco'].append(disco)
        time.sleep(intervalo)

# === Función principal ===
def main():
    try:
        print("🖥️ Iniciando monitoreo del sistema (Ctrl+C para detener)...")
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.submit(monitorear_cpu, resultados)
            executor.submit(monitorear_memoria, resultados)
            executor.submit(monitorear_disco, resultados)

            # Cada 30 segundos: calcular promedios
            while not detenerse.is_set():
                time.sleep(30)
                if all(resultados.values()):  # si hay datos acumulados
                    prom_cpu = sum(resultados['cpu']) / len(resultados['cpu'])
                    prom_mem = sum(resultados['memoria']) / len(resultados['memoria'])
                    prom_dis = sum(resultados['disco']) / len(resultados['disco'])
                    print(f"\n📊 Promedios últimos {len(resultados['cpu'])*5}s:")
                    print(f"   CPU: {prom_cpu:.2f}% | Memoria: {prom_mem:.2f}% | Disco: {prom_dis:.2f}%")

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo monitoreo...")
        detenerse.set()  # señal para finalizar los hilos
        time.sleep(2)
        print("✅ Monitoreo detenido correctamente.")

if __name__ == "__main__":
    main()
