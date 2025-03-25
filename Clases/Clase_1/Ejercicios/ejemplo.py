import sys

# Verifica que haya al menos un argumento adicional
if len(sys.argv) > 1:
    nombre = " ".join(sys.argv[1:])  # Une todos los argumentos después del nombre del script
    print(f"Hola, {nombre}!")
else:
    print("Por favor, ingresa tu nombre como argumento.")
