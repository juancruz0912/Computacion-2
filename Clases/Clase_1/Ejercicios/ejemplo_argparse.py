import argparse

# Función para validar si el estudiante está aprobado o desaprobado
def estado_estudiante(nota):
    if nota >= 6:
        return 'Aprobado'
    else:
        return 'Desaprobado'

# Función de validación de nota
def validar_nota(nota):
    try:
        # Convertir el valor a float
        valor = float(nota)
        if 1 <= valor <= 10:
            return valor
        else:
            raise argparse.ArgumentTypeError("La nota debe estar entre 1 y 10.")
    except ValueError:
        raise argparse.ArgumentTypeError("La nota debe ser un número.")

def guardar_en_archivo(nombre, apellido, materias, nota, estado):
    # Abrimos el archivo en modo 'write' para sobreescribir
    with open("estudiante.txt", "w") as archivo:
        archivo.write(f"Estudiante: {nombre} {apellido}\n")
        archivo.write(f"Materias: {', '.join(materias)}\n")
        archivo.write(f"Nota: {nota}\n")
        archivo.write(f"Estado: {estado}\n")
    print("La información se ha guardado en 'estudiante.txt'.")

def main():
    parser = argparse.ArgumentParser(description="Script de saludo")
    
    parser.add_argument("-n", "--nombre", required=True, help="Nombre del estudiante")
    parser.add_argument("-a", "--apellido", required=True, help="Apellido del estudiante")
    parser.add_argument("-m", "--materia", nargs="+", help="Materias que está cursando", default=[])
    parser.add_argument("-N", "--nota", type=validar_nota, help="Nota entre 1 y 10", required=True)

    args = parser.parse_args()

    # Calcular el estado del estudiante según la nota
    estado = estado_estudiante(args.nota)

    # Imprimir los resultados
    print(f"Estudiante: {args.nombre} {args.apellido}")
    print(f"Materias: {', '.join(args.materia)}")
    print(f"Nota: {args.nota}")
    print(f"Estado: {estado}")

    # Guardar la información en un archivo de texto
    guardar_en_archivo(args.nombre, args.apellido, args.materia, args.nota, estado)


if __name__ == "__main__":
    main()
