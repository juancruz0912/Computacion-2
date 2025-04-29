import signal
import time

# Definimos el manejador de la señal SIGALRM
def tiempo_agotado(signum, frame):
    print("\n⏰ ¡Tiempo agotado! No ingresaste nada a tiempo.")
    exit(1)  # Terminamos el programa


def main():
    # Asociamos SIGALRM con nuestra función manejadora
    signal.signal(signal.SIGALRM, tiempo_agotado)

    # Activamos una alarma para 7 segundos
    signal.alarm(7)

    # Intentamos obtener un input del usuario
    entrada = input("📥 Ingresá algo en menos de 7 segundos: ")

    # Cancelamos la alarma si el usuario responde a tiempo
    signal.alarm(0)
    print(f"✅ Ingresaste: {entrada}")


if __name__ == "__main__":
    main()