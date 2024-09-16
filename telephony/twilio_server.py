from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
import json
import uvicorn
from dotenv import load_dotenv
import os
import uvicorn
from openvoicechat.tts.tts_xtts import Mouth_xtts as Mouth
from openvoicechat.llm.llm_ollama import Chatbot_ollama as Chatbot
from openvoicechat.stt.stt_hf import Ear_hf as Ear
from openvoicechat.llm.prompts import llama_sales
from openvoicechat.utils import run_chat
from dotenv import load_dotenv
import threading
import queue
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openvoicechat.utils import Listener_ws, Player_ws
from pydub import AudioSegment
import librosa
import numpy as np
import torch


load_dotenv()

HTTP_SERVER_PORT = 8080

app = FastAPI()

if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"


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
        audio_array = librosa.resample(
            y=audio_array, orig_sr=samplerate, target_sr=self.target_sr
        )
        audio_array = audio_array.tobytes()
        audio_segment = AudioSegment(
            data=audio_array,
            sample_width=2,  # 2 bytes = 16 bits per sample (int16)
            frame_rate=self.target_sr,
            channels=1,  # Mono
        )

        # Export the AudioSegment to μ-law encoded format (this converts to μ-law)
        mulaw_audio = audio_segment.set_sample_width(1).export(format="mulaw")

        self.output_queue.put(mulaw_audio)

    def stop(self):
        self.playing = False
        self.output_queue.queue.clear()

    def wait(self):
        # TODO use the mark message to wait for the audio to finish playing
        self.playing = False


class Listener_twilio:
    def __init__(self, q, samplerate=8000):
        self.input_queue = q
        self.listening = False
        self.CHUNK = 5945
        self.RATE = 16_000
        self.samplerate = samplerate

    def read(self, x):
        data = self.input_queue.get()
        audio_segment = AudioSegment(
            data=data,
            sample_width=1,  # 8 bits for x-mulaw
            frame_rate=self.samplerate,
            channels=1,  # Mono audio
        )

        # Get PCM data as an array of samples
        pcm_data = audio_segment.get_array_of_samples()

        # Convert to a NumPy array of int16
        data = np.array(pcm_data, dtype=np.int16)
        data = librosa.resample(y=data, orig_sr=self.samplerate, target_sr=16_000)
        data = data.tobytes()
        return data

    def close(self):
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
    listener = Listener_ws(input_queue)
    player = Player_ws(output_queue)

    mouth = Mouth(player=player, device=device)
    ear = Ear(
        model_id="openai/whisper-tiny.en",
        device=device,
        silence_seconds=1.5,
        listener=listener,
    )
    load_dotenv()

    chatbot = Chatbot(sys_prompt=llama_sales, model="qwen2:0.5b")
    threading.Thread(target=run_chat, args=(mouth, ear, chatbot, True)).start()

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
                print(media["payload"])
                if listener.listening:
                    input_queue.put(media["payload"])
                if not output_queue.empty():
                    response_data = output_queue.get_nowait()
                    response_json = {
                        "event": "media",
                        "media": {"payload": response_data},
                        "streamSid": data["streamSid"],
                    }
                    await websocket.send_text(json.dumps(response_json))

            elif data["event"] == "closed":
                log("Closed Message received", message)
                break

            count += 1

    except Exception as e:
        log(f"Connection error: {e}")
    finally:
        log(f"Connection closed. Received a total of {count} messages")
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run("twilio_server:app", host="0.0.0.0", port=HTTP_SERVER_PORT, reload=True)
