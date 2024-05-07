from fastapi import FastAPI, WebSocket
import uvicorn
import asyncio
from openvoicechat.tts.tts_piper import Mouth_piper as Mouth
from openvoicechat.llm.llm_gpt import Chatbot_gpt as Chatbot
from openvoicechat.stt.stt_hf import Ear_hf as Ear
import torch
from openvoicechat.llm.prompts import llama_sales
import torchaudio
import torchaudio.functional as F
import numpy as np
import threading
import librosa
import queue
import time

app = FastAPI()


class Player_websocket:
    def __init__(self, websocket):
        self.websocket = websocket
        self.playing = False
        self.thread = None

    async def send_audio_chunks(self, audio_array, sample_rate):
        # resample using librosa
        audio_array = librosa.resample(y=audio_array, orig_sr=sample_rate, target_sr=44100)
        audio_array = audio_array.tobytes()
        CHUNK_SIZE = 4096 * 4
        for i in range(0, len(audio_array), CHUNK_SIZE):
            if not self.playing:
                break
            # print(f"Sending chunk {i}")
            await self.websocket.send_bytes(audio_array[i:i + CHUNK_SIZE])
            await asyncio.sleep((CHUNK_SIZE / 4) / 44100)

    async def play(self, audio_array, sample_rate):
        self.playing = True
        await asyncio.gather(self.send_audio_chunks(audio_array, sample_rate))
        # self.thread = threading.Thread(target=self.send_audio_chunks, args=(audio_array, sample_rate))
        # self.thread.start()

    def stop(self):
        self.playing = False
        if self.thread:
            self.thread.join()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # consumer_task = asyncio.ensure_future(receive_messages(websocket))
    # await asyncio.gather(consumer_task)
    player = Player_websocket(websocket)
    mouth = Mouth(device='cuda',
                  model_path='../models/en_US-ryan-high.onnx',
                  config_path='../models/en_en_US_ryan_high_en_US-ryan-high.onnx.json')
    audio = mouth.run_tts('Good morning!') / (1 << 15)
    audio = audio.astype(np.float32)
    print(mouth.sample_rate)
    await player.play(audio, mouth.sample_rate)


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         # Launching send and receive tasks
#         consumer_task = asyncio.ensure_future(receive_messages(websocket))
#         producer_task = asyncio.ensure_future(send_messages(websocket))
#         await asyncio.gather(consumer_task, producer_task)
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         await websocket.close()
#
#
async def receive_messages(websocket: WebSocket):
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_array = np.frombuffer(data, dtype=np.float32)
            # audio_queue.put(audio_array.tobytes())
            print(f"Received message")
    except Exception as e:
        print(f"Receive error: {e}")

#
# async def send_messages(websocket: WebSocket):
#     try:
#         await asyncio.sleep(2)  # Simulate delay
#         while True:
#             # await asyncio.sleep(0.1)  # Simulate delay
#             audio_data = audio_queue.get()
#             # audio_data = np.frombuffer(audio_data, dtype=np.int16) / (1 << 15)
#             # audio_data = audio_data.astype(np.float32)
#             await websocket.send_bytes(audio_data)
#             await asyncio.sleep(16384 / 44100)  # Simulate delay
#             print("Sent message to client.")
#     except Exception as e:
#         print(f"Send error: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
