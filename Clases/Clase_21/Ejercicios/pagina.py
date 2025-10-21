import requests
import aiohttp
import asyncio

async def descargar_async():
    # requests.get() NO es awaitable, bloquea el thread
    # response = await requests.get("http://youtube.com")  # ✗ Error
    #si saco await, funciona pero es sincrono
    
    # aiohttp.get() SÍ es awaitable, no bloquea
    async with aiohttp.ClientSession() as session:
        async with session.get("http://youtube.com.") as response:
            return await response.text()
        
async def main():
    print(await descargar_async())

if __name__ == "__main__":
    asyncio.run(main())
