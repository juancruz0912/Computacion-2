import os

def main():
    print('Simulador de pipeline')
    print('Ingrese "exit" para salir')
    comando = input('Primer comando a ejecutar: ')
    comando2 = input('Segundo comando a ejecutar: ')

    if comando == 'exit' or comando2 == 'exit':
        print('Saliendo...')
        return

    elif not comando or not comando2:
        print('Comando inválido')
        return

    else:
        r, w = os.pipe()  # Crear el pipe

        pid = os.fork()

        if pid == 0:  # Proceso hijo
            os.close(w)  # Cerrar extremo de escritura
            os.dup2(r, 0)  # Redirigir stdin al extremo de lectura del pipe
            os.close(r)  # Cerrar extremo de lectura después de redirigir
            try:
                os.execlp(comando2, comando2)  # Ejecutar el segundo comando
            except FileNotFoundError:
                print(f"Error: Comando '{comando2}' no encontrado")
                os._exit(1)

        else:  # Proceso padre
            os.close(r)  # Cerrar extremo de lectura
            os.dup2(w, 1)  # Redirigir stdout al extremo de escritura del pipe
            os.close(w)  # Cerrar extremo de escritura después de redirigir
            try:
                os.execlp(comando, comando)  # Ejecutar el primer comando
            except FileNotFoundError:
                print(f"Error: Comando '{comando}' no encontrado")
                os._exit(1)

if __name__ == '__main__':
    main()