from multiprocessing import Process, Array

def cuadrado(numeros):
    for i in range(len(numeros)):
        numeros[i] = numeros[i] * numeros[i]

if __name__ == '__main__':
    arr = Array('i', [1, 2, 3, 4])  # 'i' = enteros, 'd' = flotantes, etc
    p = Process(target=cuadrado, args=(arr,))
    p.start()
    p.join()

    print("Array al cuadrado:", list(arr))
