'''Objetivo:** Comprimir múltiples archivos en paralelo usando diferentes algoritmos.

**Requisitos:**
1. Crear 10 archivos de texto con contenido aleatorio
2. Comprimir cada uno con gzip usando ProcessPoolExecutor
3. Comparar tiempo secuencial vs paralelo
4. Calcular ratio de compresión promedio
5. Mostrar progreso: "Comprimido 3/10 archivos..."
'''

import gzip
import shutil
import time
import random
import string
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor



# Con un tamaño pequeño de archivos, tardo mas en crear los preocesos que en lo que gano en procesamiento, 
# en caso contrario, si los archivos son mas pesados, el cuello de bottela es al cpu y ahi se ve la diferencia usando procesos vs hilos
def crear_archivos(carpeta: Path, cantidad=10, tamaño_kb=100):
    carpeta.mkdir(exist_ok=True)
    for i in range(cantidad):
        ruta = carpeta / f"archivo_{i+1}.txt"
        with open(ruta, "w") as f:
            # cada archivo tendrá texto aleatorio de tamaño_kb kilobytes aprox.
            texto = ''.join(random.choices(string.ascii_letters + string.digits + " \n", k=tamaño_kb * 1024))
            f.write(texto)
    print(f"✅ Se crearon {cantidad} archivos en {carpeta}")


def comprimir_archivo(ruta_entrada: Path):
    ruta_salida = ruta_entrada.with_suffix('.gz')
    with open(ruta_entrada, 'rb') as f_in:
        with gzip.open(ruta_salida, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    return {
        'archivo': ruta_entrada.name,
        'tamaño_original': ruta_entrada.stat().st_size,
        'tamaño_comprimido': ruta_salida.stat().st_size
    }


def comprimir_secuencial(archivos):
    print("\n🕐 Compresión secuencial iniciada...")
    inicio = time.time()
    resultados = []
    for i, archivo in enumerate(archivos, start=1):
        info = comprimir_archivo(archivo)
        resultados.append(info)
        print(f"Comprimido {i}/{len(archivos)} archivos...")
    duracion = time.time() - inicio
    return resultados, duracion


def comprimir_paralelo_procesos(archivos):
    print("\n Compresión paralela iniciada...")
    inicio = time.time()
    resultados = []
    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(comprimir_archivo, archivo): archivo for archivo in archivos}
        for i, future in enumerate(as_completed(futures), start=1):
            info = future.result()  # bloquea hasta que ese proceso termina
            resultados.append(info)
            print(f"Comprimido {i}/{len(archivos)} archivos...")
    duracion = time.time() - inicio
    return resultados, duracion

def comprimir_paralelo_hilos(archivos):
    print("\n Compresión paralela iniciada...")
    inicio = time.time()
    resultados = []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(comprimir_archivo, archivo): archivo for archivo in archivos}
        for i, future in enumerate(as_completed(futures), start=1):
            info = future.result()  # bloquea hasta que ese proceso termina
            resultados.append(info)
            print(f"Comprimido {i}/{len(archivos)} archivos...")
    duracion = time.time() - inicio
    return resultados, duracion


def calcular_ratio_promedio(resultados):
    ratios = [r['tamaño_comprimido'] / r['tamaño_original'] for r in resultados]
    return sum(ratios) / len(ratios)


# --- Programa principal ---
if __name__ == "__main__":
    carpeta = Path("archivos_prueba")
    crear_archivos(carpeta)

    archivos = list(carpeta.glob("*.txt"))

    # Secuencial
    resultados_seq, t_seq = comprimir_secuencial(archivos)
    ratio_seq = calcular_ratio_promedio(resultados_seq)

    # Paralelo procesos
    resultados_par, t_par_p = comprimir_paralelo_procesos(archivos)
    ratio_par_p = calcular_ratio_promedio(resultados_par)
    
    # Paralelo hilos
    resultados_par, t_par_i = comprimir_paralelo_hilos(archivos)
    ratio_par_i = calcular_ratio_promedio(resultados_par)

    print("\n📊 RESULTADOS FINALES:")
    print(f"Tiempo secuencial: {t_seq:.2f} s")
    print(f"Tiempo paralelo_procesos:   {t_par_p:.2f} s")
    print(f"Tiempo paralelo_hilos:   {t_par_i:.2f} s")
    print(f"Ratio promedio secuencial: {ratio_seq:.2f}")
    print(f"Ratio promedio paralelo (procesos):   {ratio_par_p:.2f}")
    print(f"Ratio promedio paralelo (hilos):   {ratio_par_i:.2f}")


