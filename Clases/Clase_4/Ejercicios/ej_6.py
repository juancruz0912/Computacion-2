#Crea un "servidor" de operaciones matemáticas usando pipes. 
#El proceso cliente envía operaciones matemáticas como cadenas (por ejemplo, "5 + 3", "10 * 2"), 
#y el servidor las evalúa y devuelve el resultado. Implementa manejo de errores para operaciones inválidas.

import os

def operaciones_matematicas(operacion):
    try:
        return eval(operacion)
    except Exception as e:
        return None, f"Operación ({operacion}) inválida: {str(e)}"
    
def main():
    r, w = os.pipe()
    pid = os.fork()
    
    if pid == 0:  # Proceso hijo
        os.close(w)  # Cerrar extremo de escritura
        try:
            operacion = os.read(r, 1024).decode()
            resultado, error = operaciones_matematicas(operacion)
            if resultado is not None:
                print(f'La operación matemática es: {operacion} y el resultado es: {resultado}\n')        
            else:
                print(error)
        except Exception as e:
            print(f"Error: {str(e)}")
        os.close(r)
        os._exit(0)

    else:  # Proceso padre
        os.close(r)  # Cerrar extremo de lectura
        try:
            operacion = input('Operación matemática: ')
            os.write(w, operacion.encode())
        except Exception as e:
            print(f"Error: {str(e)}")
        os.close(w)
        os.wait()

if __name__ == "__main__":
    main()