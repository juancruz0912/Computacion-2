from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def tarea(x):
    return x * 2

# Puedes intercambiarlos fácilmente
for ExecutorClass in [ThreadPoolExecutor, ProcessPoolExecutor]:
    with ExecutorClass(max_workers=4) as executor:
        resultados = executor.map(tarea, range(10))
        print(executor, list(resultados))