from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()
@app.get("/")
async def get():
    return HTMLResponse(open('voice_chat.html', 'r').read())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_bytes()
        print(data)
        await websocket.send_text(f"Message text was: {data}")


if __name__ == "__main__":
    uvicorn.run(app, port=8000)