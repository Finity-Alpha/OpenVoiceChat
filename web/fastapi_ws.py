from fastapi import FastAPI, WebSocket
import uvicorn
import numpy as np
import wave
import soundfile as sf


app = FastAPI()


@app.websocket("/ws")
async def receive_audio(websocket: WebSocket):
    await websocket.accept()
    all_data = b''
    while True:
        data = await websocket.receive_bytes()
        all_data += data
        audio_array = np.frombuffer(all_data, dtype=np.float32)
        sf.write("audio_data.wav", audio_array, 44100)

## NOTES:
# The above function receives the audio data from the websocket
# If we can make a stream out of this data, we can easily
# integrate it with the existing codebase
# data = stream.read(CHUNK)
# data = websocket.read()



@app.websocket("/ws/audio")
async def send_audio(websocket: WebSocket):
    await websocket.accept()
    wav_file = wave.open('abs.wav', 'rb')
    audio_data = wav_file.readframes(wav_file.getnframes())
    framerate = wav_file.getframerate()
    wav_file.close()
    print(len(audio_data), framerate)
    audio_data = np.frombuffer(audio_data, dtype=np.int16) / (1 << 15)
    audio_data = audio_data.astype(np.float32)
    await websocket.send_bytes(audio_data.tobytes())

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
