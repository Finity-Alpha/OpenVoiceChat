from fastapi import FastAPI, WebSocket
import uvicorn
from openvoicechat.tts.tts_piper import Mouth_piper as Mouth
from openvoicechat.llm.llm_gpt import Chatbot_gpt as Chatbot
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
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"))


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
        self.output_queue.put('stop'.encode())

    def wait(self):
        time_to_wait = 0
        # while not self.output_queue.empty():
        #     time.sleep(0.1)
        #     peek at the first element
            # time_to_wait = len(self.output_queue.queue[0]) / (44100 * 4)
        # print(time_to_wait)
        # time.sleep(time_to_wait)
        self.playing = False


class Listener_ws:
    def __init__(self, q):
        self.input_queue = q
        self.listening = False
        self.CHUNK = 5945
        self.RATE = 16_000

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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print('connected')
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
                # print(len(data))
                input_queue.put(data)
            if not output_queue.empty():
                response_data = output_queue.get_nowait()
            else:
                response_data = 'none'.encode()
            await websocket.send_bytes(response_data)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
        del mouth
        del ear
        #clear cuda cache
        import torch
        torch.cuda.empty_cache()
    finally:
        await websocket.close()

@app.get("/")
def read_root():
    return FileResponse('static/stream_audio.html')
if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
