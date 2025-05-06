from multiprocessing import Process, Queue

def hijo(q):
    q.put("Mensaje desde el hijo")

if __name__ == '__main__':
    q = Queue()
    p = Process(target=hijo, args=(q,))
    p.start()

    print("Padre recibió:", q.get())
    p.join()
