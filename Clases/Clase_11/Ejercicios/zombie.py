'''
Cree un script en Python que genere un proceso hijo que finaliza inmediatamente. 
El padre no deberá recolectar su estado hasta al menos 10 segundos después.

Desde Bash, utilice ps y /proc/[pid]/status para identificar el estado Z (zombi) del hijo.
'''

import os
import time

if __name__ == "__main__":
    pid = os.fork()
    if pid == 0:
        print(f"Soy el proceso hijo (PID: {os.getpid()}) y el PID de mi padre es {os.getppid()}")
        os._exit(0)
    else:
        time.sleep(30)
        os.wait()
    

'''
resultado:
cat /proc/52972/status
Name:	python3
State:	Z (zombie)
'''