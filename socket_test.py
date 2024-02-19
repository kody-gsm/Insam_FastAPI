import json
import asyncio
import websockets
import sys
from websockets.exceptions import ConnectionClosedError
import asyncio
import time

USER_NAME = '1112345678999'

BACKEND_URL = '116.124.89.131:8000'
LOCAL_URL = '127.0.0.1:8000'

async def handle_input():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, "Enter something asynchronously: ")

async def ws_send(ws):
    while True:
        message = {'type': "test", 'message' : "Hello, WebSocket"}
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
    url = f"ws://{LOCAL_URL}/ws/{USER_NAME}"
    print(url)
    try:
        async with websockets.connect(url, ping_interval=60, extra_headers={"client_id": "code"}) as websocket:

            asyncio.create_task(ws_send(websocket))

            while True:
                recv_task = asyncio.create_task(ws_recv(websocket))

                await recv_task

    except ConnectionClosedError as e:
        print(f"WebSocket connection closed unexpectedly: {e}")


asyncio.run(main())