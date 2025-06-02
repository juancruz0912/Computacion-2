from multiprocessing import Process, Semaphore, Queue, current_process
import time
import random

def producer_sem_pc(queue, empty_sem, full_sem): # Renombrado
    """ Produce 10 items y los pone en la cola. """
    for i in range(10):
        item = f"Item-{i} by {current_process().name}"
        
        empty_sem.acquire() # Espera si el buffer está lleno (no hay 'empty' slots)
        print(f"Productor {current_process().name}: Produciendo {item}")
        queue.put(item)
        time.sleep(random.uniform(0.1, 0.3))
        full_sem.release() # Señala que hay un 'full' slot más

def consumer_sem_pc(queue, empty_sem, full_sem): # Renombrado
    """ Consume 10 items de la cola. """
    for _ in range(10):
        full_sem.acquire() # Espera si el buffer está vacío (no hay 'full' slots)
        item = queue.get()
        print(f"Consumidor {current_process().name}: Consumiendo {item}")
        time.sleep(random.uniform(0.2, 0.5))
        empty_sem.release() # Señala que hay un 'empty' slot más

if __name__ == '__main__':
    buffer_size_sem = 5 # Renombrado
    queue_sem = Queue(buffer_size_sem) # Renombrado
    
    empty_s = Semaphore(buffer_size_sem) # Renombrado
    full_s = Semaphore(0) # Renombrado

    p_sem = Process(target=producer_sem_pc, args=(queue_sem, empty_s, full_s), name="P-Sem")
    c_sem = Process(target=consumer_sem_pc, args=(queue_sem, empty_s, full_s), name="C-Sem")

    p_sem.start()
    c_sem.start()

    p_sem.join()
    c_sem.join()
    print("Sistema Productor-Consumidor (Semaphore) terminado.")