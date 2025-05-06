from multiprocessing import Pool
import os, time

def cubo(n):
    time.sleep(5)
    resultados = n * n * n
    print(f'soy el proceso {os.getpid()} y el cubo de {n} es {resultados}')
    return resultados

if __name__ == '__main__':
    print(os.getpid())
    time.sleep(15)
    numeros = [1, 2, 3, 4, 5]
    with Pool(processes=3) as pool:
        resultados = pool.map(cubo, numeros)

    print("Resultados:", resultados)
