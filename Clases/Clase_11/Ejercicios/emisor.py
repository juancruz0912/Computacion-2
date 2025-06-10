'''
Cree un FIFO en /tmp/mi_fifo usando Bash (mkfifo). Luego:

    Escriba un script emisor.py que escriba mensajes en el FIFO.
    Escriba un script receptor.py que lea desde el FIFO e imprima los mensajes.

Ejecute ambos scripts en terminales distintas.
'''


if __name__ == "__main__":
    for i in range(5):
        mensaje = f'Este es el mensaje {i}'
        with open("/tmp/mi_fifo", "w") as f:
            f.write(mensaje)
        print(mensaje)
        

# Primero se debe ejecutar receptor.py para que no se bloquee este proceso al no haber nadie escuchando

