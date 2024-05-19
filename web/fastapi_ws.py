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


class Listener:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.queue = queue.Queue()
        self.loop = asyncio.get_event_loop()
        self.listening = False
        self.thread = None
        self.future = None

    async def read_audio_chunks(self):
        await asyncio.sleep(0.1)
        print('created task')
        while self.listening:
            data = await self.websocket.receive_bytes()
            print('data yay')
            # await asyncio.sleep(0.1)
            data = np.frombuffer(data, dtype=np.float32)
            data = librosa.resample(y=data, orig_sr=44100, target_sr=16_000)
            data = data * (1 << 15)
            data = data.astype(np.int16)
            data = data.tobytes()
            self.queue.put(data)

    def thread_function(self):
        # Set up a new event loop for the thread.
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # loop.run_until_complete(self.read_audio_chunks())
        # loop.close()
        print('thread here')
        coro = self.read_audio_chunks()
        print(coro)
        asyncio.run_coroutine_threadsafe(coro, self.loop)
        # asyncio.run_coroutine_threadsafe(asyncio.sleep(0.1), self.loop)
        print('should be run')
        # self.future.result(3)

    def make_stream(self):
        self.listening = True
        self.thread = threading.Thread(target=self.thread_function, args=())
        self.thread.start()
        return self

    def read(self):
        assert self.listening, 'Run make_stream'
        # print('reading')
        # data = await self.websocket.receive_bytes()
        # data = np.frombuffer(data, dtype=np.float32)
        # data = librosa.resample(y=data, orig_sr=44100, target_sr=16_000)
        # data = data * (1 << 15)
        # data = data.astype(np.int16)
        # data = data.tobytes()
        # queue.put(data)
        # while self.queue.empty():
        #     time.sleep(0.1)
        # return b''
        try:
            return self.queue.get(block=False)
        except queue.Empty:
            return b''
        # return self.queue.get(block=False)
        # return data

    def close(self):
        self.listening = False
        # try:
        #     self.future.result(1)
        # except asyncio.TimeoutError:
        #     print('timeout')
        self.thread.join()
        self.queue.queue.clear()


ear = Ear(device='cuda', silence_seconds=2)




@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    print('accepted')
    player = Player_websocket(websocket)
    listener = Listener(websocket)
    assert listener.loop is asyncio.get_event_loop()
    while True:
        stream = listener.make_stream()
        await asyncio.sleep(1)
        # print(id(asyncio.get_running_loop()))
        # data = await websocket.receive_bytes()
        # print(len(data), type(data))
        #
        # mouth = Mouth(device='cuda',
        #               model_path='../models/en_US-ryan-high.onnx',
        #               config_path='../models/en_en_US_ryan_high_en_US-ryan-high.onnx.json',
        #               player=player)
        # load_dotenv()
        # chatbot = Chatbot(api_key=os.getenv('OPENAI_API_KEY'), sys_prompt='You are a helpful assistant')
        frames = []
        # loop = asyncio.get_event_loop()
        # nest_asyncio.apply()
        # q = queue.Queue()
        # print(asyncio.all_tasks())
        print('listening')
        maximum = 3 * 5
        i = 0
        while i < maximum:
            # coro = asyncio.create_task(asyncio.sleep(0.1))
            await asyncio.sleep(0.1)
            # future = asyncio.ensure_future(asyncio.create_task(asyncio.sleep(0.05)))
            # listener.loop.run_until_complete(coro)


            # future = asyncio.run_coroutine_threadsafe(asyncio.sleep(0.05), listener.loop)
            # future.result(timeout=1000)

            # data = await stream.read()
            # task = loop.create_task(stream.read())
            # asyncio.create_task(coro())
            # asyncio.run_coroutine_threadsafe(stream.read(q), loop)
            # while q.empty():
            #     time.sleep(0.1)
            data = stream.read()
            #
            if len(data) == 0:
                continue
            frames.append(data)
            # frames.append(b'0')
            i += 1
        stream.close()
        frames = np.frombuffer(b''.join(frames), dtype=np.int16)
        frames = frames / (1 << 15)

        frames = frames.astype(np.float32)
        print(ear.transcribe(frames))

        # run_chat(mouth, ear, chatbot)


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
