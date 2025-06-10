import os
import argparse
import time
import random

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--num", type=int, required=True)
    parser.add_argument("--verbose", type=bool, default=False)
    args = parser.parse_args()
    cant_procesos = args.num
    
    # Guardar el PID del proceso original
    pid_original = os.getpid()
    
    if args.verbose:
        print(args.verbose)
        mensaje = 'Mensaje especial'
    else:
        mensaje = ''
    
    print(f"Soy el proceso padre (PID: {pid_original}) y el PID de mi hijo es {pid_original}.")
    # Crear todos los hijos
    for i in range(cant_procesos):
        pid = os.fork()
        if pid == 0:
            time.sleep(random.randint(1, 5))
            print(f"Soy el proceso hijo (PID: {os.getpid()}) y el PID de mi padre es {pid_original}. {mensaje}")
            os._exit(0)
        else:
            if i == cant_procesos - 1:
                print("\nJerarquía de procesos:")
                os.system(f"pstree -p {pid_original}")
    
    # Esperar a que todos los hijos terminen
    for i in range(cant_procesos):
        os.wait()
    