import time
from concurrent.futures import ProcessPoolExecutor, as_completed


def es_primo(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2): #verifica divisores impares hasta la raiz cuadrada
        if n % i == 0:
            return False
    return True


def encontrar_primos_en_rango(inicio, fin):
    return [n for n in range(inicio, fin) if es_primo(n)]


def primos_secuencial(rango_inicio=1, rango_fin=1_000_000):
    print("\n🕐 Buscando primos (secuencial)...")
    inicio = time.time()
    primos = encontrar_primos_en_rango(rango_inicio, rango_fin)
    duracion = time.time() - inicio
    print(f"✔️  Encontrados {len(primos)} primos.")
    return primos, duracion

def primos_paralelo(rango_inicio=1, rango_fin=1_000_000, chunks=100):
    print("\n⚙️ Buscando primos (paralelo con procesos)...")

    # Crear los chunks
    tamaño_chunk = (rango_fin - rango_inicio) // chunks
    rangos = []

    for i in range(chunks):
        ini = rango_inicio + i * tamaño_chunk
        fin = rango_inicio + (i + 1) * tamaño_chunk
        if i == chunks - 1: 
            fin = rango_fin
        rangos.append((ini, fin))


    inicio = time.time()
    primos = []

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(encontrar_primos_en_rango, ini, fin): (ini, fin) for ini, fin in rangos}
        for i, future in enumerate(as_completed(futures), start=1):
            resultado = future.result()
            primos.extend(resultado)
            if i % 10 == 0 or i == len(futures):
                print(f"Completado {i}/{len(futures)} chunks...")

    duracion = time.time() - inicio
    print(f"✔️  Encontrados {len(primos)} primos.")
    return primos, duracion


# --- Programa principal ---
if __name__ == "__main__":
    # Secuencial
    primos_seq, t_seq = primos_secuencial()

    # Paralelo
    primos_par, t_par = primos_paralelo()

    # Comparar tiempos
    print("\n📊 RESULTADOS:")
    print(f"Tiempo secuencial: {t_seq:.2f} s")
    print(f"Tiempo paralelo (procesos): {t_par:.2f} s")
    print(f"Cantidad de primos (ambos): {len(primos_seq)}")
    print(f"Cantidad de primos (ambos): {len(primos_par)}")

