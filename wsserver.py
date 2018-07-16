import asyncio

import websockets


class WSServer:
    connected = set()
    queue = asyncio.Queue()

    async def handler(self, websocket: websockets.WebSocketServerProtocol, path):
        # Register.
        self.connected.add(websocket)
        try:
#            await asyncio.wait([ws.send("Hello!" + str(len(self.connected))) for ws in self.connected])
            while True:
                data = await self.queue.get()
                await websocket.send(data)
        except Exception as e:
            print(e)
        finally:
            # Unregister.
            print(websocket, 'disconnected')
            self.connected.remove(websocket)

    async def send_all(self, msg):
        if len(self.connected) > 0:
            await self.queue.put(msg)
        # print(self.queue.qsize())

    async def run(self):
        await websockets.serve(self.handler, '0.0.0.0', 5678)


srv = WSServer()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(srv.run())
    loop.run_forever()
