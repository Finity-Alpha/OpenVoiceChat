if __name__ == "__main__":
    from base import BaseEar
else:
    from .base import BaseEar
import os
from dotenv import load_dotenv
import websockets
import json
import asyncio


class Ear_deepgram(BaseEar):
    def __init__(self, silence_seconds=2, api_key="", listener=None):
        super().__init__(silence_seconds, stream=True, listener=listener)
        self.api_key = api_key

    def transcribe_stream(self, audio_queue, transcription_queue):
        extra_headers = {"Authorization": "token " + self.api_key}

        async def f():
            async with websockets.connect(
                "wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=16000"
                "&channels=1&model=nova-2",
                extra_headers=extra_headers,
            ) as ws:

                async def sender(ws):  # sends audio to websocket
                    try:
                        while True:
                            data = audio_queue.get()
                            if data is None:
                                await ws.send(json.dumps({"type": "CloseStream"}))
                                break
                            await ws.send(data)
                    except Exception as e:
                        print("Error while sending: ", str(e))
                        raise

                async def receiver(ws):
                    async for msg in ws:
                        msg = json.loads(msg)
                        if "channel" not in msg:
                            transcription_queue.put(None)
                            break
                        transcript = msg["channel"]["alternatives"][0]["transcript"]

                        if transcript:
                            transcription_queue.put(transcript)

                await asyncio.gather(sender(ws), receiver(ws))

        asyncio.run(f())


if __name__ == "__main__":
    import torchaudio
    import torchaudio.functional as F

    ear = Ear_deepgram()
    #
    # audio, sr = torchaudio.load('../media/abs.wav')
    # audio = F.resample(audio, sr, 16_000)[0]
    # text = ear.transcribe(np.array(audio))
    # print(text)

    text = ear.listen()
    print(text)
