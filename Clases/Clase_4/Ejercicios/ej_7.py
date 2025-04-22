# Implementa un sistema donde múltiples procesos "generadores" crean transacciones (operaciones con un ID, tipo y monto), 
# las envían a un proceso "validador" que verifica su integridad, y finalmente 
# a un proceso "registrador" que acumula las estadísticas. Usa múltiples pipes 
# para manejar este flujo complejo y asegúrate de manejar correctamente la sincronización y el cierre de la comunicación.

import os
import json
import time

def crear_transaccion(w, i):
    print('-----------------------------------------------------')
    print('Ingrese "Exit" para salir')
    print(f'Creando transferencia {i}...')
    tipo = input('Tipo de transferencia: ')
    if tipo == 'Exit':
        return 0
    monto = input('Monto: ')
    mensaje = {'ID': os.getpid(), 'tipo': tipo, 'monto': monto}
    time.sleep(3)
    os.write(w, json.dumps(mensaje).encode())  # Enviar datos como JSON
    print(f'Datos de la transferencia enviados: {mensaje}')
    os.close(w)  # Cerrar extremo de escritura
    return 1

def validar(r, w):
    datos = os.read(r, 1024).decode()
    os.close(r)  # Cerrar extremo de lectura del pipe de entrada
    try:
        if datos:
            transferencia = json.loads(datos)  # Decodificar JSON
            print(f'Transferencia recibida para validación: {transferencia}')
            if transferencia.get('tipo') and transferencia.get('monto'):
                print('Transferencia válida')
                mensaje = 'OK'
        else:
            print('Transferencia rechazada')
            mensaje = 'ERROR'
        os.write(w, mensaje.encode())  # Enviar resultado de validación
    except Exception as e:
        print(f'Error al validar transferencia: {e}')
        mensaje = 'ERROR'
        os.write(w, mensaje.encode())
    os.close(w)  # Cerrar extremo de escritura del pipe de salida

def registrar(r):
    mensaje = os.read(r, 1024).decode()
    if mensaje == "OK":
        print('Registrando transferencia...')
        time.sleep(3)
        print(f'Transferencia válida registrada')
    else:
        print(f'Transferencia rechazada')
    os.close(r)  # Cerrar extremo de lectura

def main():
    i = 0
    while True:
        r1, w1 = os.pipe()  # Pipe entre crear_transaccion y validar
        r2, w2 = os.pipe()  # Pipe entre validar y registrar

        i += 1

        pid1 = os.fork() # Modificaar esto para que varias las transacciones se vayan enviando y se vayan verificando varias al "mismo tiempo"
        if pid1 == 0:  # Proceso hijo 1: crear_transaccion
            os.close(r1)  # Cerrar extremo de lectura del primer pipe
            os.close(r2)  # Cerrar extremos no utilizados
            os.close(w2)
            if crear_transaccion(w1, i) == 0:
                os._exit(0)  # Señal de salida para el padre
            os._exit(1)  # Señal de continuar para el padre

        else:
            pid2 = os.fork()
            if pid2 == 0:  # Proceso hijo 2: validar
                os.close(w1)  # Cerrar extremo de escritura del primer pipe
                os.close(r2)  # Cerrar extremo de lectura del segundo pipe
                validar(r1, w2)
                os._exit(0)

            else:  # Proceso padre
                os.close(w1)  # Cerrar extremos no utilizados
                os.close(r1)
                os.close(w2)
                registrar(r2)

                # Esperar a que los hijos terminen
                _, status = os.wait()  # Esperar al proceso hijo 1
                if os.WEXITSTATUS(status) == 0:  # Si el hijo devuelve 0, salir del bucle
                    break
                os.wait()  # Esperar al proceso hijo 2

if __name__ == '__main__':
    main()
