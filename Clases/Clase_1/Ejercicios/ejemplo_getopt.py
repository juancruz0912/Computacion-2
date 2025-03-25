import sys
import getopt

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "n:a:e:", ["nombre=", "apellido=", "edad="])
    except getopt.GetoptError as err:
        print(f"Error: {err}")
        sys.exit(1)

    nombre = None
    apellido = None
    edad = None

    for opt, arg in opts:
        if opt in ("-n", "--nombre"):
            nombre = arg
        elif opt in ("-a", "--apellido"):
            apellido = arg
        elif opt in ("-e", "--edad"):
            edad = arg

    if nombre and apellido and edad:
        print(f"Hola, {nombre} {apellido}! Tienes {edad} años.")
    else:
        print("Uso: python ejemplo_getopt.py -n Juan -a Perez -e 25")

if __name__ == "__main__":
    main()
