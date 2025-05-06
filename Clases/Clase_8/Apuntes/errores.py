from multiprocessing import Pool

def dividir(n):
    if n == 0:
        raise ValueError("No se puede dividir por cero")
    return 10 / n

if __name__ == '__main__':
    with Pool(3) as pool:
        resultados = [pool.apply_async(dividir, args=(i,)) for i in [5, 3, 0, 2]]

        for r in resultados:
            try:
                print(r.get())  # Aquí puede lanzarse la excepción
            except Exception as e:
                print(f"Ocurrió un error: {e}")
