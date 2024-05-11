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

app = FastAPI()


class Player_websocket:
    def __init__(self, websocket):
        self.thread = None
        self.websocket = websocket
        self.playing = False
        self.play_task = None
        self.audio_array_queue = queue.Queue()

    async def send_audio_chunks(self, sample_rate):
        # resample using librosa
        while self.playing:
            try:
                # Wait for audio data to be available in the queue
                data = self.audio_array_queue.get(block=False)  # Adjust timeout as needed
                audio_array = librosa.resample(y=data, orig_sr=sample_rate, target_sr=44100)
                audio_array = audio_array.tobytes()
                await self.websocket.send_bytes(audio_array)
            except queue.Empty:
                break

    def thread_function(self, sample_rate):
        # Set up a new event loop for the thread.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.send_audio_chunks(sample_rate))
        finally:
            loop.close()

    def play(self, audio_array, samplerate):
        audio_array = audio_array / (1 << 15)
        audio_array = audio_array.astype(np.float32)
        self.audio_array_queue.put(audio_array)
        self.playing = True
        # self.thread = threading.Thread(target=self.send_audio_chunks, args=(samplerate,))
        self.thread = threading.Thread(target=self.thread_function, args=(samplerate,))
        self.thread.start()

    def stop(self):
        self.playing = False
        if self.thread:
            self.thread.join()

    def wait(self):
        self.thread.join()
        self.playing = False


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        print('accepted')
        data = await websocket.receive_bytes()

        player = Player_websocket(websocket)
        mouth = Mouth(device='cuda',
                      model_path='../models/en_US-ryan-high.onnx',
                      config_path='../models/en_en_US_ryan_high_en_US-ryan-high.onnx.json',
                      player=player)
        ear = Ear(device='cuda', silence_seconds=2)
        load_dotenv()
        chatbot = Chatbot(api_key=os.getenv('OPENAI_API_KEY'), sys_prompt='You are a helpful assistant')
        run_chat(mouth, ear, chatbot)


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
