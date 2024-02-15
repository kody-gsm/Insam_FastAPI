import json
import asyncio
import websockets
import sys
from websockets.exceptions import ConnectionClosedError
import asyncio
import time

USER_NAME = '1112345678999'

BACKEND_URL = '192.168.1.5:8000'
LOCAL_URL = '127.0.0.1:8000'

async def handle_input():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, "Enter something asynchronously: ")

async def ws_send(ws):
    while True:
        message = {'message' : "Hello, WebSocket", 'type': "test"}
        await ws.send(json.dumps(message))
        await asyncio.sleep(0.2)
        # while True:
        #     text = await handle_input()
        #     if text:
        #         message = {'message' : text, 'type': "test"}
        #         text = False
        #         await ws.send(json.dumps(message))
        #         await asyncio.sleep(0.2)


async def ws_recv(ws):
    response_text_data = await ws.recv()
    if response_text_data != False:
        response = json.loads(response_text_data)
        print(response)
        response_text_data = False


async def main():
    url = f"ws://{BACKEND_URL}/ws/{USER_NAME}"
    print(url)
    try:
        async with websockets.connect(url, ping_interval=60) as websocket:

            asyncio.create_task(ws_send(websocket))

            while True:
                task = asyncio.create_task(ws_recv(websocket))

                await task

    except ConnectionClosedError as e:
        print(f"WebSocket connection closed unexpectedly: {e}")


asyncio.run(main())