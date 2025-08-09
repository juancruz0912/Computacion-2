'''
Implemente dos scripts:

    generador.py: genera una serie de números aleatorios (parámetro --n) y los imprime por salida estándar.
    filtro.py: recibe números por entrada estándar y muestra solo los mayores que un umbral (parámetro --min).

Desde Bash, encadene la salida del primero a la entrada del segundo:
'''

import random 
import argparse

#
parser = argparse.ArgumentParser(description="Genera números aleatorios")
parser.add_argument("--n", type=int, required=True, help="Cantidad de números a generar")
args = parser.parse_args()


for i in range(args.n):
    print(random.randint(1, 10)) # generate numbers between 1 and 10
