import asyncio
import websockets
import sounddevice as sd
import numpy as np
import pyaudio
import json
import queue
import threading


class WebSocketAudioClient:
    def __init__(self, uri):
        self.uri = uri
        self.chunk = 1024  # Buffer size
        self.sample_rate = 44100  # Sample rate
        self.p = pyaudio.PyAudio()

    def play_audio(self, audio_queue):
        while True:
            audio_data = audio_queue.get()
            if audio_data == "none":
                break
            audio_array = np.array(audio_data)
            sd.play(audio_array, self.sample_rate)
            sd.wait()

    async def send_audio(self):
        async with websockets.connect(self.uri) as websocket:
            stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk,
            )

            print("Recording and sending audio...")
            stream.start_stream()

            try:
                while stream.is_active():
                    audio_json = {"type": "stt", "data": stream.read(self.chunk)}
                    await websocket.send(json.dumps(audio_json))
            except KeyboardInterrupt:
                print("Stopped by user")
            finally:
                stream.stop_stream()
                stream.close()

    async def receive_audio(self):
        audio_queue = queue.Queue()
        message_queue = queue.Queue()
        threading.Thread(target=self.play_audio, args=(audio_queue,)).start()
        async with websockets.connect(self.uri) as websocket:
            print("Receiving audio...")
            while True:
                message = await websocket.recv()
                message_json = json.loads(message)
                if message_json["type"] == "tts":
                    audio_queue.put(message_json["data"])
                elif message_json["type"] == "action":
                    if message_json["data"] == "stop":
                        audio_queue.queue.clear()
                        audio_queue.put("none")
                        break

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(self.send_audio(), self.receive_audio()))


# Example usage
# client = WebSocketAudioClient("ws://localhost:8000/ws")
# client.run()
