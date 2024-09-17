from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
import json
import uvicorn
import os
import uvicorn
from openvoicechat.tts.tts_xtts import Mouth_xtts as Mouth
from openvoicechat.llm.llm_gpt import Chatbot_gpt as Chatbot
from openvoicechat.stt.stt_hf import Ear_hf as Ear
from openvoicechat.llm.prompts import llama_sales
from openvoicechat.utils import run_chat
from dotenv import load_dotenv
import threading
import queue
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydub import AudioSegment
import librosa
import numpy as np
import torch
import base64
import audioop

load_dotenv()

HTTP_SERVER_PORT = 8080

app = FastAPI()

if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"
print(f"Using device: {device}")


load_dotenv()


def log(msg, *args):
    print(f"Media WS: ", msg, *args)


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


class Player_twilio:
    def __init__(self, q, target_sr=8000):
        self.output_queue = q
        self.playing = False
        self.target_sr = 8000

    def play(self, audio_array, samplerate):
        self.playing = True
        if audio_array.dtype == np.int16:
            audio_array = audio_array / (1 << 15)
        audio_array = audio_array.astype(np.float32)
        data = librosa.resample(
            y=audio_array, orig_sr=samplerate, target_sr=self.target_sr
        )
        data = data * (1 << 15)
        data = data.astype(np.int16)
        ulaw_audio = audioop.lin2ulaw(data.tobytes(), 2)
        payload = base64.b64encode(ulaw_audio).decode()

        self.output_queue.put(payload)

    def stop(self):
        self.playing = False
        self.output_queue.queue.clear()
        self.output_queue.put("stop")

    def wait(self):
        while self.playing:
            pass


class Listener_twilio:
    def __init__(self, q, samplerate=8000):
        self.input_queue = q
        self.listening = False
        self.CHUNK = 320
        self.RATE = 16_000
        self.samplerate = samplerate

    def read(self, x):
        data = base64.b64decode(self.input_queue.get())
        pcm_audio = audioop.ulaw2lin(data, 2)  # '2' indicates 16-bit PCM

        data = np.frombuffer(pcm_audio, dtype=np.int16)
        data = data / (1 << 15)  # TODO: make the conversions faster
        data = data.astype(np.float32)
        data = librosa.resample(y=data, orig_sr=self.samplerate, target_sr=16_000)
        data = data * (1 << 15)
        data = data.astype(np.int16)
        data = data.tobytes()
        return data

    def close(self):
        self.listening = False
        pass

    def make_stream(self):
        self.listening = True
        self.input_queue.queue.clear()
        return self


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    log("Connection accepted")
    input_queue = queue.Queue()
    output_queue = queue.Queue()
    listener = Listener_twilio(input_queue)
    player = Player_twilio(output_queue)

    mouth = Mouth(player=player, device=device)
    ear = Ear(
        model_id="openai/whisper-base.en",
        device=device,
        silence_seconds=1,
        listener=listener,
        listen_interruptions=True,
    )
    load_dotenv()

    chatbot = Chatbot(sys_prompt=llama_sales)
    threading.Thread(
        target=run_chat,
        args=(mouth, ear, chatbot, True, lambda x: False, "Hello, I am John."),
    ).start()

    mark_queue = []
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
                if listener.listening:
                    input_queue.put(media["payload"])
            elif data["event"] == "mark":
                name = int(data["mark"]["name"])
                mark_queue.remove(name)
                if len(mark_queue) == 0:
                    player.playing = False

            if not output_queue.empty():
                response_data = output_queue.get_nowait()
                if response_data == "stop":
                    response_json = {
                        "event": "clear",
                        "streamSid": data["streamSid"],
                    }
                    await websocket.send_text(json.dumps(response_json))
                else:
                    response_json = {
                        "event": "media",
                        "media": {"payload": response_data},
                        "streamSid": data["streamSid"],
                    }
                    mark_queue.append(max(mark_queue) + 1 if mark_queue else 0)
                    mark_message = {
                        "event": "mark",
                        "streamSid": data["streamSid"],
                        "mark": {"name": f"{mark_queue[-1]}"},
                    }
                    await websocket.send_text(json.dumps(response_json))
                    await websocket.send_text(json.dumps(mark_message))

            elif data["event"] == "closed":
                log("Closed Message received", message)
                break

    except Exception as e:
        log(f"Connection error: {e}")
    finally:
        await websocket.close()
        # TODO: join thread and close gracefully


if __name__ == "__main__":
    uvicorn.run(
        "twilio_server:app", host="0.0.0.0", port=HTTP_SERVER_PORT, reload=False
    )
