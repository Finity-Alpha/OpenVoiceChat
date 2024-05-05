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
import queue

device = 'cuda' if torch.cuda.is_available() else 'cpu'
audio_queue = queue.Queue()

print('loading models... ', device)

ear = Ear(silence_seconds=2, device=device)
audio, sr = torchaudio.load('media/my_voice.wav')
audio = F.resample(audio, sr, 16_000)[0]
# ear.transcribe(np.array(audio))

john = Chatbot(sys_prompt=llama_sales)

mouth = Mouth(device=device)
mouth.say_text('Good morning!')

print("type: exit, quit or stop to end the chat")
print("Chat started:")
pre_interruption_text = ''
while True:
    user_input = pre_interruption_text + ' ' + ear.listen()
    if user_input.lower() in ["exit", "quit", "stop"]:
        break
    print(user_input)

    llm_output_queue = queue.Queue()
    interrupt_queue = queue.Queue()
    llm_thread = threading.Thread(target=john.generate_response_stream,
                                  args=(user_input,
                                        llm_output_queue,
                                        interrupt_queue))

    tts_thread = threading.Thread(target=mouth.say_multiple_stream,
                                  args=(llm_output_queue,
                                        ear.interrupt_listen,
                                        interrupt_queue,
                                        audio_queue))

    llm_thread.start()
    tts_thread.start()

    tts_thread.join()
    llm_thread.join()
    if not interrupt_queue.empty():
        pre_interruption_text = interrupt_queue.get()

    res = llm_output_queue.get()
    print('res ', res)
    if '[END]' in res:
        break


app = FastAPI()



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Launching send and receive tasks
        consumer_task = asyncio.ensure_future(receive_messages(websocket))
        producer_task = asyncio.ensure_future(send_messages(websocket))
        await asyncio.gather(consumer_task, producer_task)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()


async def receive_messages(websocket: WebSocket):
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_array = np.frombuffer(data, dtype=np.float32)
            # audio_queue.put(audio_array.tobytes())
            print(f"Received message")
    except Exception as e:
        print(f"Receive error: {e}")


async def send_messages(websocket: WebSocket):
    try:
        await asyncio.sleep(2)  # Simulate delay
        while True:
            # await asyncio.sleep(0.1)  # Simulate delay
            audio_data = audio_queue.get()
            # audio_data = np.frombuffer(audio_data, dtype=np.int16) / (1 << 15)
            # audio_data = audio_data.astype(np.float32)
            await websocket.send_bytes(audio_data)
            await asyncio.sleep(16384/44100)  # Simulate delay
            print("Sent message to client.")
    except Exception as e:
        print(f"Send error: {e}")


#
# @app.websocket("/ws")
# async def receive_audio(websocket: WebSocket):
#     await websocket.accept()
#     all_data = b''
#     while True:
#         data = await websocket.receive_bytes()
#         print('received')
#         all_data += data
#         audio_array = np.frombuffer(all_data, dtype=np.float32)
#         audio_queue.put(audio_array.tobytes())
#         # sf.write("audio_data.wav", audio_array, 44100)
#
# ## NOTES:
# # The above function receives the audio data from the websocket
# # If we can make a stream out of this data, we can easily
# # integrate it with the existing codebase
# # data = stream.read(CHUNK)
# # data = websocket.read()
#
#
#
# @app.websocket("/ws/audio")
# async def send_audio(websocket: WebSocket):
#     await websocket.accept()
#     # wav_file = wave.open('abs.wav', 'rb')
#     # audio_data = wav_file.readframes(wav_file.getnframes())
#     # framerate = wav_file.getframerate()
#     # wav_file.close()
#     # print(len(audio_data), framerate)
#     await websocket.send_bytes(np.zeros(44100).tobytes())
#     while True:
#         audio_data = audio_queue.get()
#         print('sending', audio_data)
#         audio_data = np.frombuffer(audio_data, dtype=np.int16) / (1 << 15)
#         audio_data = audio_data.astype(np.float32)
#         await websocket.send_bytes(audio_data.tobytes())

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
