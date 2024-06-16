import uvicorn
from openvoicechat.tts.tts_elevenlabs import Mouth_elevenlabs as Mouth
from openvoicechat.llm.llm_gpt import Chatbot_gpt
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
import torch

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

device = 'cuda' if torch.cuda.is_available() else 'cpu'


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print('connected')

    input_queue = queue.Queue()
    output_queue = queue.Queue()
    listener = Listener_ws(input_queue)
    player = Player_ws(output_queue)

    mouth = Mouth(player=player, voice_id='IKne3meq5aSn9XLyUdCD')
    ear = Ear(device=device, silence_seconds=2,
              listener=listener)
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
    uvicorn.run(app, host='0.0.0.0', port=8000,
                ssl_keyfile="localhost+2-key.pem", ssl_certfile="localhost+2.pem")
