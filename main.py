from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.get("/")
def home():
    return "hello word"

@app.websocket("/{flowerpot_id}")
async def test(websocket:WebSocket, flowerpot_id:str):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(data)
        if data == "exit":
            await websocket.close()
            break

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)