from multiprocessing import Pool

def saludar(nombre):
    return f"Hola, {nombre}"

if __name__ == '__main__':
    with Pool(processes=2) as pool:
        resultado1 = pool.apply_async(saludar, args=("Juan",))
        resultado2 = pool.apply_async(saludar, args=("Ana",))
        
        print(resultado1.get())  # Espera resultado
        print(resultado2.get())
