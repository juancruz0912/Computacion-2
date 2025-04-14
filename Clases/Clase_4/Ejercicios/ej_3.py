# Crea una cadena de tres procesos conectados por pipes donde: 
# el primer proceso genera números aleatorios entre 1 y 100, 
# el segundo proceso filtra solo los números pares, y el tercer proceso calcula el cuadrado de estos números pares.

import os 
import random

def numeros_aleatorios(cantidad = 10):
    numeros = []
    for i in range(cantidad):
        numeros.append(random.randint(1, 100))
    return numeros 

def numeros_pares(numero):
    return numero % 2 == 0

def cuadrado(numero):
    numero = int(numero)
    return numero ** 2
    

def main():
    r1, w1 = os.pipe()
    r2, w2 = os.pipe()

    pid = os.fork()

    if pid == 0:  # Primer hijo, segundo proceso
# Cerrar los canales del pipe que no usaremos
        os.close(w1)
        os.close(r2)

        # Leer del pipe
        numeros = os.read(r1, 1024).decode()  # Leer todos los números como una cadena
        for numero in numeros.splitlines():  # Dividir la cadena en líneas (números individuales)
            print(f"[HIJO] Recibí el número: {numero}, tipo: {type(numero)}")
            if numeros_pares(int(numero)):  # Convertir a entero y verificar si es par
                    os.write(w2, f"{numero}\n".encode())  # Enviar número par al segundo pipe
                    print(f"[HIJO 1] El número {numero} es par")
                
        # Cerrar los extremos restantes
        os.close(r1)
        os.close(w2)
        os._exit(0)

    else:
        pid2 = os.fork()

        if pid2 == 0:  # Segundo hijo, tercer proceso
            
            # Cerrar los canales del pipe que no usaremos
            os.close(w1)
            os.close(r1)
            os.close(w2)

            # Leer del pipe
            numeros = os.read(r2, 1024).decode()  # Leer todos los números como una cadena
            for numero in numeros.splitlines():  # Dividir la cadena en líneas (números individuales)
                resultado = cuadrado(int(numero))  # Convertir a entero y calcular el cuadrado
                print(f"[HIJO 2] El cuadrado de {numero} es {resultado}")

            # Cerrar el canal que no usaremos
            os.close(r2)
            os._exit(0)

        else:  # Proceso padre, primer proceso
            os.close(r1)
            os.close(r2)
            os.close(w2)

            # Generar números aleatorios y enviarlos
            numeros = numeros_aleatorios(13)
            print('[PADRE] Números generados:', numeros)
            for numero in numeros:
                os.write(w1, f"{numero}\n".encode())  # Enviar cada número como una línea separada
                print(f"[PADRE] Enviando número: {numero}")

            # Cerrar el canal que no usaremos y esperar a los hijos
            os.close(w1)
            os.wait()
            os.wait()

if __name__ == "__main__":
    main()