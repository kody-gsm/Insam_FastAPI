import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.protocols.utils import ClientDisconnected
import asyncio
import json
import base64
import cv2
import numpy as np

import logging

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler()])


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin을 허용하거나, 필요한 경우 특정 origin만 허용할 수 있습니다.
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드를 허용하거나 필요한 메서드만 허용할 수 있습니다.
    allow_headers=["*"],  # 모든 헤더를 허용하거나 필요한 헤더만 허용할 수 있습니다.
)

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://${window.location.host}/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(JSON.stringify({
                    type: 'test',
                    message: input.value
                }))
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    i = 0
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        await self.broadcast({"type": "welcome", "message": client_id})
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        logger.info(f"WebSocket disconnected: {websocket}")
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_json(message)
        except WebSocketDisconnect:
            print('dksl')

    async def broadcast(self, message: dict):
        print(self.i)
        self.i = self.i + 1
        for connection in self.active_connections:
            if connection.state != WebSocketState.DISCONNECTED:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect as we:
                    print(f"WebSocketDisconnect error: {we}")
                except ClientDisconnected:
                    print("tlqkf")
                    await manager.disconnect(connection)
                except Exception as e:
                    print(f"Exception: {e}")
                    print(f"Exception type: {type(e)}")



manager = ConnectionManager()


async def cam(frame):
    cv2.imshow('dk', frame)
    cv2.waitKey(0)

@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)

    print(websocket.scope)


    try:
        while True:
            data = await websocket.receive_json()

            ws_type = data['type']
            message = data['message']

            if ws_type == 'image':
                image_str = bytes(message, 'utf-8')
                image = base64.b64decode(image_str)
                frame = cv2.imdecode(np.frombuffer(image, np.uint8), 1)

            await manager.broadcast(data)


    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        # await manager.broadcast({"message" : f"Client #{client_id} left the chat", "type": "disconnect"})