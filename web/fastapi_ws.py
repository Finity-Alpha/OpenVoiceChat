from fastapi import FastAPI, WebSocket
import uvicorn
import asyncio
from openvoicechat.tts.tts_piper import Mouth_piper as Mouth
from openvoicechat.llm.llm_gpt import Chatbot_gpt as Chatbot
from openvoicechat.stt.stt_hf import Ear_hf as Ear
from openvoicechat.llm.prompts import llama_sales
from openvoicechat.utils import run_chat
from dotenv import load_dotenv
import os
import librosa
import threading

app = FastAPI()


class Player_websocket:
    def __init__(self, websocket, loop):
        self.websocket = websocket
        self.playing = False
        self.play_task = None
        self.audio_array_queue = asyncio.Queue()
        self.loop = loop

    async def send_audio_chunks(self, audio_array, sample_rate):
        print('run function')
        # resample using librosa
        audio_array = librosa.resample(y=audio_array, orig_sr=sample_rate, target_sr=44100)
        audio_array = audio_array.tobytes()
        CHUNK_SIZE = 4096 * 4
        for i in range(0, len(audio_array), CHUNK_SIZE):
            if not self.playing:
                break
            print(f"Sending chunk {i}")
            await self.websocket.send_bytes(audio_array[i:i + CHUNK_SIZE])
            await asyncio.sleep((CHUNK_SIZE / 4) / 44100)

    async def _play(self, audio_array, sample_rate):
        self.playing = True
        await asyncio.gather(self.send_audio_chunks(audio_array, sample_rate))
        #
        # def run_in_thread():
        #     # Create a new event loop for the thread
        #     try:
        #         # Run the coroutine in this new event loop
        #         self.loop.run_until_complete(self.send_audio_chunks(audio_array, sample_rate))
        #     finally:
        #         self.loop.close()
        #
        # # Start the thread
        # self.thread = threading.Thread(target=run_in_thread)
        # self.thread.start()

        # self.thread = threading.Thread(target=self.send_audio_chunks, args=(audio_array, sample_rate))
        # self.thread.start()

    def play(self, audio_array, samplerate):
        task = asyncio.run_coroutine_threadsafe(self._play(audio_array, samplerate), self.loop)
        print('task created', task)
        self.play_task = task

    def stop(self):
        self.playing = False
        if self.play_task:
            self.play_task.cancel()

    async def wait(self):
        print('waiting')
        self.play_task.result()


load_dotenv()

loop = asyncio.new_event_loop()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print('accepted')
    # make asyncio loop

    player = Player_websocket(websocket, loop)
    mouth = Mouth(device='cuda',
                  model_path='../models/en_US-ryan-high.onnx',
                  config_path='../models/en_en_US_ryan_high_en_US-ryan-high.onnx.json',
                  player=player)
    device = 'cuda'

    print('loading models... ', device)

    ear = Ear(silence_seconds=2, device=device)

    api_key = os.getenv('OPENAI_API_KEY')

    chatbot = Chatbot(sys_prompt=llama_sales, api_key=api_key)
    run_chat(mouth, ear, chatbot, verbose=True)
    # audio = mouth.run_tts('Good morning!') / (1 << 15)
    # audio = audio.astype(np.float32)
    # print(mouth.sample_rate)
    # player.play(audio, mouth.sample_rate)
    # await player.wait()


# async def receive_messages(websocket: WebSocket):
#     try:
#         while True:
#             data = await websocket.receive_bytes()
#             audio_array = np.frombuffer(data, dtype=np.float32)
#             # audio_queue.put(audio_array.tobytes())
#             print(f"Received message")
#     except Exception as e:
#         print(f"Receive error: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
