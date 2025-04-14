# Implementa un sistema donde múltiples procesos "generadores" crean transacciones (operaciones con un ID, tipo y monto), 
# las envían a un proceso "validador" que verifica su integridad, y finalmente 
# a un proceso "registrador" que acumula las estadísticas. Usa múltiples pipes 
# para manejar este flujo complejo y asegúrate de manejar correctamente la sincronización y el cierre de la comunicación.

import os
import json

def crear_transaccion(w):
    print('Creando transferencia...')
    tipo = input('Tipo de transferencia: ')
    monto = input('Monto: ')
    mensaje = {'ID': os.getpid(), 'tipo': tipo, 'monto': monto}
    os.write(w, json.dumps(mensaje).encode())  # Enviar datos como JSON
    print(f'Datos de la transferencia enviados: {mensaje}')
    os.close(w)  # Cerrar extremo de escritura

def validar(r, w):
    os.close(w)  # Cerrar extremo de escritura del pipe de entrada
    datos = os.read(r, 1024).decode()
    os.close(r)  # Cerrar extremo de lectura del pipe de entrada

    if datos:
        transferencia = json.loads(datos)  # Decodificar JSON
        print(f'Transferencia recibida para validación: {transferencia}')
        # Validar transferencia (aquí puedes agregar más validaciones si es necesario)
        if transferencia.get('tipo') and transferencia.get('monto'):
            mensaje = 'OK'
        else:
            mensaje = 'ERROR'
    else:
        mensaje = 'ERROR'

    os.write(w, mensaje.encode())  # Enviar resultado de validación
    os.close(w)  # Cerrar extremo de escritura del pipe de salida

def registrar(r):
    os.close(r)  # Cerrar extremo de escritura del pipe de entrada
    while True:
        mensaje = os.read(r, 1024).decode()
        if not mensaje:
            break
        print(f'Registrando transferencia: {mensaje}')
    os.close(r)  # Cerrar extremo de lectura

def main():
    r1, w1 = os.pipe()  # Pipe entre crear_transaccion y validar
    r2, w2 = os.pipe()  # Pipe entre validar y registrar

    pid1 = os.fork()
    if pid1 == 0:  # Proceso hijo 1: crear_transaccion
        os.close(r1)  # Cerrar extremo de lectura del primer pipe
        os.close(r2)  # Cerrar extremos no utilizados
        os.close(w2)
        crear_transaccion(w1)
        os._exit(0)

    pid2 = os.fork()
    if pid2 == 0:  # Proceso hijo 2: validar
        os.close(w1)  # Cerrar extremo de escritura del primer pipe
        os.close(r2)  # Cerrar extremo de lectura del segundo pipe
        validar(r1, w2)
        os._exit(0)

    # Proceso padre: registrar
    os.close(w1)  # Cerrar extremos no utilizados
    os.close(r1)
    os.close(w2)
    registrar(r2)

    # Esperar a que los hijos terminen
    os.wait()
    os.wait()

if __name__ == '__main__':
    main()
