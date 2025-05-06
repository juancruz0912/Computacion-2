from multiprocessing import Process, Pipe
import os, time

def hijo(conn):
    conn.send("Hola desde el hijo")
    print(os.getpid())
    time.sleep(30)
    conn.close()

if __name__ == '__main__':
    padre_conn, hijo_conn = Pipe()
    p = Process(target=hijo, args=(hijo_conn,))
    p.start()

    print("Padre recibió:", padre_conn.recv())
    p.join()
