from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import Response
import json
import uvicorn
from dotenv import load_dotenv
import os
import uvicorn
import base64
import audioop
import sounddevice as sd
import numpy as np

load_dotenv()

HTTP_SERVER_PORT = 8080

app = FastAPI()


def log(msg, *args):
    pass


@app.post("/twiml")
async def return_twiml():
    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
      <Connect>
        <Stream url="{os.environ.get("TWILIO_SERVER_URL")}"></Stream>
      </Connect>
      <Pause length="40"/>
    </Response>"""
    return Response(content=xml_content, media_type="application/xml")


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    log("Connection accepted")
    data = b""
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            if data["event"] == "connected":
                log("Connected Message received", message)
            elif data["event"] == "start":
                log("Start Message received", message)
            elif data["event"] == "media":
                media = data["media"]
                print(str(media) + ",")
                # audio = base64.b64decode(media["payload"])
                # data += audio
            elif data["event"] == "closed":
                log("Closed Message received", message)
                break

    except Exception as e:
        log(f"Connection error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(
        "twilio_listen_server:app", host="0.0.0.0", port=HTTP_SERVER_PORT, reload=False
    )
