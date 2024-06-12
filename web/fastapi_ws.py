import sys
import os

# Add the project directory to the sys.path
sys.path.append('/home/centrox/Documents/OpenVoiceChat')

import uvicorn
from openvoicechat.tts.tts_hf import Mouth_hf as Mouth
# from openvoicechat.llm.llm_llama import Chatbot_llama as Chatbot
from openvoicechat.llm.base import BaseChatbot
from openvoicechat.stt.stt_hf import Ear_hf as Ear
from openvoicechat.llm.prompts import llama_sales
from openvoicechat.utils import run_chat
from dotenv import load_dotenv
import os
import threading
import queue
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openvoicechat.utils import Listener_ws, Player_ws
from together import Together
class Chatbot_gpt(BaseChatbot):
    def __init__(self, sys_prompt='', Model='togethercomputer/Llama-2-7B-32K-Instruct'):
        load_dotenv()
        Togethers = os.getenv("togethers")
        self.MODEL = Model
        self.client = Together(api_key=Togethers)
        self.messages = []
        self.messages.append({"role": "system", "content": sys_prompt})

    def run(self, input_text):
        self.messages.append({"role": "user", "content": input_text})

        stream = self.client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=self.messages,
            stream=True,
)
        print()
        for chunk in stream:
            
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def post_process(self, response):
        self.messages.append({"role": "assistant", "content": response})
        return response
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")




@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print('connected')
    input_queue = queue.Queue()
    output_queue = queue.Queue()
    listener = Listener_ws(input_queue)
    player = Player_ws(output_queue)
    mouth = Mouth(device='cpu', player=player, forward_params={"speaker_id": 10})
    ear = Ear(device='cpu', silence_seconds=1, listener=listener)
    load_dotenv()

    chatbot = Chatbot_gpt(sys_prompt=llama_sales)
    threading.Thread(target=run_chat, args=(mouth, ear, chatbot, True)).start()

    try:
        while True:
            data = await websocket.receive_bytes()
            if listener.listening:
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
