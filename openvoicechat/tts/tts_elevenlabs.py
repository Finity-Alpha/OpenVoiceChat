if __name__ == '__main__':
    from base import BaseMouth
else:
    from .base import BaseMouth
from dotenv import load_dotenv
from pydub import AudioSegment
import io
import numpy as np
import sounddevice as sd
import requests
import os


class Mouth_elevenlabs(BaseMouth):
    def __init__(self, model_id='eleven_turbo_v2',
                 voice_id='IKne3meq5aSn9XLyUdCD',
                 api_key='',
                 optimize_stream_latency=4):
        self.model_id = model_id
        self.voice_id = voice_id
        self.api_key = api_key
        self.optimize_stream_latency = optimize_stream_latency
        super().__init__(sample_rate=44100)

    def run_tts(self, text):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}?optimize_streaming_latency={self.optimize_stream_latency}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": f"{self.api_key}"
        }

        data = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        response = requests.post(url, json=data, headers=headers)
        try:
            audio_segment = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
        except Exception as e:
            print(response.content)
            print(f"Error: {e}")
            return None

        samples = np.array(audio_segment.get_array_of_samples())

        return samples


if __name__ == '__main__':
    load_dotenv()
    mouth = Mouth_elevenlabs(api_key=os.getenv('ELEVENLABS_API_KEY'))

    text = ("If there's one thing that makes me nervous about the future of self-driving cars, it's that they'll "
            "replace human drivers.\nI think there's a huge opportunity to make human-driven cars safer and more "
            "efficient. There's no reason why we can't combine the benefits of self-driving cars with the ease of use "
            "of human-driven cars.")
    print(text)
    mouth.say_multiple(text, lambda x: False)
    sd.wait()
