'''
Implemente un script que use fork() para crear un proceso hijo. 
Ese hijo deberá reemplazar su imagen de ejecución por el comando ls -l usando exec().

Desde Bash, verifique el reemplazo observando el nombre del proceso con ps.
'''

import os
import time

if __name__ == "__main__":
    pid = os.fork()
    if pid == 0:
        time.sleep(5)  
        os.execvp("ls", ["ls", "-l"])
    else:
        time.sleep(10) 
        os.wait()


'''
resultado:

-> % ps aux | grep python

juanx      56257  0.3  0.0  16468  7900 pts/0    S+   17:08   0:00 python3 exec.py
juanx      56258  0.0  0.0  16468  2820 pts/0    S+   17:08   0:00 python3 exec.py
juanx      56261  0.0  0.0   6356  2132 pts/6    S+   17:08   0:00 grep --color=auto --exclude-dir=.bzr --exclude-dir=CVS --exclude-dir=.git --exclude-dir=.hg --exclude-dir=.svn --exclude-dir=.idea --exclude-dir=.tox --exclude-dir=.venv --exclude-dir=venv python

-> % ps aux | grep python

juanx      56257  0.1  0.0  16468  7900 pts/0    S+   17:08   0:00 python3 exec.py
juanx      56346  0.0  0.0   6356  2216 pts/6    S+   17:08   0:00 grep --color=auto --exclude-dir=.bzr --exclude-dir=CVS --exclude-dir=.git --exclude-dir=.hg --exclude-dir=.svn --exclude-dir=.idea --exclude-dir=.tox --exclude-dir=.venv --exclude-dir=venv python

-> % ps -ef | grep ls

juanx      56258   56257  0 17:08 pts/0    00:00:00 [ls] <defunct>

'''