import os

fifo_send = 'fifo_a_b'
fifo_recv = 'fifo_b_a'

print("[A] Chat iniciado. Escribí 'salir' para terminar.")

while True:
    # Enviar mensaje
    msg = input("[A]: ")
    with open(fifo_send, 'w') as f:
        f.write(msg + '\n')
        f.flush() #obligar al sistema operativo a que escriba en memoria

    if msg == 'salir':
        break

    # Esperar respuesta
    with open(fifo_recv, 'r') as f:
        respuesta = f.readline().strip()
        if respuesta == 'salir':
            print("[B] salió del chat.")
            break
        print("[B]:", respuesta)
