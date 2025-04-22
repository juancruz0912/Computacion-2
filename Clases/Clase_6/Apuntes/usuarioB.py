import os

fifo_send = 'fifo_b_a'
fifo_recv = 'fifo_a_b'

print("[B] Chat iniciado. Escribí 'salir' para terminar.")

while True:
    # Esperar mensaje
    print('Esperando mensaje de [A]...')
    with open(fifo_recv, 'r') as f:
        mensaje = f.readline().strip()
        if mensaje == 'salir':
            print("[A] salió del chat.")
            break
        print("[A]:", mensaje)

    # Responder
    msg = input("[B]: ")
    with open(fifo_send, 'w') as f:
        f.write(msg + '\n')

    if msg == 'salir':
        break
