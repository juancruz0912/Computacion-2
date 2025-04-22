import os

def leer(fifo_read):
    with open(fifo_read, 'r') as fr:
        mensaje = fr.readline().strip()
        print(f"[2] Mensaje recibido: {mensaje}")
        return mensaje


def escribir(fifo_write):
    with open(fifo_write, 'w') as fw:
        mensaje = input("[2] Mensaje a enviar: ")
        fw.write(mensaje + '\n')
        fw.flush()
        return mensaje

if __name__ == "__main__":
    fifo_write = "/tmp/chat2to1"
    fifo_read = "/tmp/chat1to2"

    if not os.path.exists(fifo_write):
        os.mkfifo(fifo_write)

    if not os.path.exists(fifo_read):
        os.mkfifo(fifo_read)
    
    print('Bienvenido al chat de usuario 2, para salir escribe exit')
    a = input('Quien empieza [1 o 2]: ')
    with open(fifo_write, 'w') as fw:
        fw.write(a + '\n')
        fw.flush()
    
    while True:
        if a == '1':
            if leer(fifo_read) == 'exit':
                break
            escribir(fifo_write)
        else:
            if escribir(fifo_write) == 'exit':
                break
            leer(fifo_read)