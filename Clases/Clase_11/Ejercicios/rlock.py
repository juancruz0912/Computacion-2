'''

Ejercicio 10: Sincronización con RLock

Diseñe una clase CuentaBancaria con métodos depositar y retirar, ambos protegidos con un RLock. 
Permita que estos métodos se llamen recursivamente (desde otros métodos sincronizados).

Simule accesos concurrentes desde varios procesos.
'''

from multiprocessing import Process, RLock
import random

class CuentaBancaria:
    def __init__(self):
        self.balance =  0
        self.rlock = RLock()

    def depositar(self, cantidad):
        with self.rlock:
            for i in range(random.randint(1, 10)):
                self.balance += cantidad
                print(f"Deposito: {cantidad}, Balance: {self.balance}")
                self.retirar(i * 10)

    def retirar(self, cantidad):
        with self.rlock:
            if self.balance >= cantidad:
                self.balance -= cantidad
                print(f"Retiro: {cantidad}, Balance: {self.balance}")
            else:
                print("Fondos insuficientes")

if __name__ == '__main__':
    cuenta = CuentaBancaria()
    
    Procesos= [Process(target=cuenta.depositar, args=(100,))]

    for p in Procesos: p.start()
    for p in Procesos: p.join()
    