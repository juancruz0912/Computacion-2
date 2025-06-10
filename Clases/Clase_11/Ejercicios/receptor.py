'''
Cree un FIFO en /tmp/mi_fifo usando Bash (mkfifo). Luego:

    Escriba un script emisor.py que escriba mensajes en el FIFO.
    Escriba un script receptor.py que lea desde el FIFO e imprima los mensajes.

Ejecute ambos scripts en terminales distintas.
'''


if __name__ == "__main__":
    for i in range(5):
        with open("/tmp/mi_fifo", "r") as f:
            mensaje = f.read()
        print(mensaje)
        