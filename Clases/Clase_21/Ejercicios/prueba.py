import asyncio
import time

async def mi_corrutina():
    return 42

async def main():
    # Esto es un awaitable (es una corrutina)
    resultado = await mi_corrutina()  # ✓ Funciona
    print(f"Resultado: {resultado}")

    # Para usar sleep de forma asíncrona, usa asyncio.sleep
    await time.sleep(1)  # ✗ TypeError: object float can't be used in 'await' expression
   #await asyncio.sleep(1)  # ✓ Funciona
    print("Después de 1 segundo")

# Ejecutar la función asíncrona principal
if __name__ == "__main__":
    asyncio.run(main())