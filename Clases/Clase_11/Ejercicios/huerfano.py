'''
Diseñe un script que cree un proceso hijo que siga ejecutándose luego 
de que el proceso padre haya terminado. Verifique desde Bash que el nuevo PPID del proceso hijo corresponde a init o systemd.
'''

import os
import time

if __name__ == "__main__":
    pid = os.fork()
    if pid == 0:
        print(f"Soy el proceso hijo (PID: {os.getpid()}) y el PID de mi padre es {os.getppid()}")
        time.sleep(30)
        os._exit(0)
    else:
        time.sleep(10)
        os.exit(0)

'''
resultado:

-> % ps -eo pid,ppid,stat,cmd | grep python

  54449    4794 S+   python3 huerfano.py
  54450   54449 S+   python3 huerfano.py
  54452   51600 S+   grep --color=auto --exclude-dir=.bzr --exclude-dir=CVS --exclude-dir=.git --exclude-dir=.hg --exclude-dir=.svn --exclude-dir=.idea --exclude-dir=.tox --exclude-dir=.venv --exclude-dir=venv python

-> % ps -eo pid,ppid,stat,cmd | grep python

  54450    1686 S    python3 huerfano.py
  54499   51600 S+   grep --color=auto --exclude-dir=.bzr --exclude-dir=CVS --exclude-dir=.git --exclude-dir=.hg --exclude-dir=.svn --exclude-dir=.idea --exclude-dir=.tox --exclude-dir=.venv --exclude-dir=venv python

-> % ps -p 1686 -o pid,ppid,stat,cmd
    PID    PPID STAT CMD
   1686       1 Ss   /lib/systemd/systemd --user

'''