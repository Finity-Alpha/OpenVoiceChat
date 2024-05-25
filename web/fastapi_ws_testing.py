from fastapi import FastAPI, WebSocket
import uvicorn
import asyncio
from openvoicechat.tts.tts_piper import Mouth_piper as Mouth
from openvoicechat.llm.llm_gpt import Chatbot_gpt as Chatbot
# from openvoicechat.llm.llm_llama import Chatbot_llama as Chatbot
from openvoicechat.stt.stt_hf import Ear_hf as Ear
from openvoicechat.llm.prompts import llama_sales
from openvoicechat.utils import run_chat
from dotenv import load_dotenv
import os
import librosa
import threading
import numpy as np
import queue
import time
import matplotlib.pyplot as plt
import nest_asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


class Player_ws:
    def __init__(self, q):
        self.output_queue = q
        self.playing = False

    def play(self, audio_array, samplerate):
        audio_array = audio_array / (1 << 15)
        audio_array = audio_array.astype(np.float32)
        audio_array = librosa.resample(y=audio_array, orig_sr=samplerate, target_sr=44100)
        audio_array = audio_array.tobytes()
        self.output_queue.put(audio_array)

    def stop(self):
        self.playing = False
        self.output_queue.queue.clear()

    def wait(self):
        while not self.output_queue.empty():
            time.sleep(0.05)
        self.playing = False


class Listener_ws:
    def __init__(self, q):
        self.input_queue = q
        self.listening = False

    def read(self, x):
        data = self.input_queue.get()
        data = np.frombuffer(data, dtype=np.float32)
        data = librosa.resample(y=data, orig_sr=44100, target_sr=16_000)
        data = data * (1 << 15)
        data = data.astype(np.int16)
        data = data.tobytes()
        return data

    def close(self):
        pass

    def make_stream(self):
        self.listening = True
        self.input_queue.queue.clear()
        return self


#     def listen(self):
#         while True:
#             data = self.input_queue.get()
#             text = ear.transcribe(data)
#             self.input_queue.task_done()
#             return text
# # output_queue = queue.Queue()
# input_queue = queue.Queue()


def transcribe(ear, listener):
    listener.listening = True
    frames = []
    print('listening')
    maximum = 3 * 5
    i = 0
    while i < maximum:
        data = listener.read()
        #
        # if len(data) == 0:
        #     continue
        frames.append(data)
        # frames.append(b'0')
        i += 1
    frames = np.frombuffer(b''.join(frames), dtype=np.int16)
    frames = frames / (1 << 15)

    frames = frames.astype(np.float32)
    print(ear.transcribe(frames))
    # data = listener.read()
    # text = ear.transcribe(data)
    # return text


def play_text(mouth, player, text):
    # mouth = Mouth()
    audio_array = mouth.run_tts(text)
    sample_rate = mouth.sample_rate
    player.play(audio_array, sample_rate)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    input_queue = queue.Queue()
    output_queue = queue.Queue()
    listener = Listener_ws(input_queue)
    player = Player_ws(output_queue)
    mouth = Mouth(model_path='../models/en_US-ryan-high.onnx',
                  config_path='../models/en_en_US_ryan_high_en_US-ryan-high.onnx.json',
                  device='cuda', player=player)
    ear = Ear(device='cuda', silence_seconds=2, listener=listener)
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    chatbot = Chatbot(sys_prompt=llama_sales,
                      api_key=api_key)
    # run transcribe in thread
    # threading.Thread(target=transcribe, args=(ear, listener)).start()
    # threading.Thread(target=play_text, args=(mouth, player, 'Hello, my name is John.')).start()
    threading.Thread(target=run_chat, args=(mouth, ear, chatbot, True)).start()

    try:
        while True:
            data = await websocket.receive_bytes()
            if listener.listening:
                input_queue.put(data)
            if not output_queue.empty():
                response_data = output_queue.get_nowait()
            else:
                response_data = np.zeros(1024, dtype=np.float32).tobytes()
            await websocket.send_bytes(response_data)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
