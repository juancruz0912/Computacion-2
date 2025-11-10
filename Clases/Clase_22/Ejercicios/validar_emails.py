import random
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import dns.resolver
import time


def generar_emails(cantidad=100):
    dominios_validos = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    dominios_invalidos = ["noexiste123.com", "dominiofake.xyz", "prueba.invalido"]
    emails = []

    for i in range(cantidad):
        if random.random() < 0.7:
            dominio = random.choice(dominios_validos) # 70% de emails validos
        else:
            dominio = random.choice(dominios_invalidos)
        emails.append(f"user{i}@{dominio}")
    return emails


def verificar_email(email):
    try:
        dominio = email.split('@')[1]
        dns.resolver.resolve(dominio, 'MX') # DNS lookup (I/O-bound)
        return (email, 'valido')
    except:
        return (email, 'invalido')


def validar_emails_secuencial(emails):
    print("\n🕐 Validando emails (secuencial)...")
    inicio = time.time()
    resultados = [verificar_email(email) for email in emails]
    duracion = time.time() - inicio
    return resultados, duracion


def validar_emails_concurrente(emails, max_workers=20, timeout=5):
    print("\n⚙️ Validando emails (paralelo con hilos)...")
    inicio = time.time()
    resultados = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(verificar_email, email): email for email in emails}
        for i, future in enumerate(as_completed(futures), start=1):
            try:
                email, estado = future.result(timeout=timeout)
                resultados.append((email, estado))
            except TimeoutError:
                resultados.append((futures[future], 'no verificable'))
            print(f"Verificado {i}/{len(emails)} emails...")
    duracion = time.time() - inicio
    return resultados, duracion


def clasificar_resultados(resultados):
    clasificados = {'valido': [], 'invalido': [], 'no verificable': []}
    for email, estado in resultados:
        clasificados[estado].append(email)
    return clasificados


if __name__ == "__main__":
    emails = generar_emails()

    # Secuencial
    resultados_seq, t_seq = validar_emails_secuencial(emails)

    # Paralelo
    resultados_thr, t_thr = validar_emails_concurrente(emails)

    # Clasificar
    clasificados = clasificar_resultados(resultados_thr)

    print("\n📊 RESULTADOS:")
    print(f"Tiempo secuencial: {t_seq:.2f} s")
    print(f"Tiempo paralelo (hilos): {t_thr:.2f} s")
    print(f"Válidos: {len(clasificados['valido'])}")
    print(f"Inválidos: {len(clasificados['invalido'])}")
    print(f"No verificables: {len(clasificados['no verificable'])}")
