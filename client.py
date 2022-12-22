import asyncio
import websockets

async def client():
    url = 'ws://localhost:5000'
    async with websockets.connect(url) as ws:
        data = input('Enter command: ')
        await ws.send(data)
        res = await ws.recv()
        print(res)

if __name__ == '__main__':
    asyncio.run(client())