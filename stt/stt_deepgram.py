if __name__ == '__main__':
    from base import BaseEar
else:
    from .base import BaseEar
import os
from dotenv import load_dotenv
import websockets
import json
import asyncio

print()
print()


class Ear_deepgram(BaseEar):
    def __init__(self, silence_seconds=2):
        super().__init__(silence_seconds)
        load_dotenv()
        self.api_key = os.getenv('DEEPGRAM_API_KEY')

    def transcribe_stream(self, audio_queue, transcription_queue):
        extra_headers = {
           'Authorization': 'token ' + self.api_key
        }
        stop = False
        async def f():
            async with websockets.connect('wss://api.deepgram.com/v1/listen?encoding=linear16&sample_rate=16000&channels=1',
                                          extra_headers=extra_headers) as ws:
                async def sender(ws):  # sends audio to websocket
                    try:
                        while True:
                            data = audio_queue.get()
                            if data is None:
                                break
                            await ws.send(data)
                    except Exception as e:
                        print('Error while sending: ', str(e))
                        raise
                    global stop
                    stop = True

                async def receiver(ws):
                    global stop
                    all_transcript = ''
                    async for msg in ws:
                        msg = json.loads(msg)
                        transcript = msg['channel']['alternatives'][0]['transcript']
                        all_transcript += transcript

                        if transcript:
                            transcription_queue.put(all_transcript)
                        if stop:
                            break

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

    text = ear.listen_stream()
    print(text)
