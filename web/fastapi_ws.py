import uvicorn
from openvoicechat.tts.tts_piper import Mouth_piper as Mouth
from openvoicechat.llm.llm_gpt import Chatbot_gpt as Chatbot
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

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"))


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
