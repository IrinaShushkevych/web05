import asyncio
import websockets

async def client():
    url = 'ws://localhost:5000'
    while True:
        async with websockets.connect(url) as ws:
            data = input('command: ')
            if data == 'exit':
                quit()
            await ws.send(data)
            res = await ws.recv()
            print(res)

if __name__ == '__main__':
    asyncio.run(client())