import torch
from tortoise.api_fast import TextToSpeech
from tortoise.utils.audio import load_voice
import sounddevice as sd
import queue
import threading
import re

def play_audio_paralell(audio_queue, sample_rate, listen_interruption_func):
    while True:
        chunk = audio_queue.get()
        if chunk is None:
            break
        chunk = chunk.cpu().numpy()
        sd.play(chunk, samplerate=sample_rate)
        duration = len(chunk) / sample_rate
        # sd.play(output, samplerate=self.model.config.sampling_rate)
        interruption = listen_interruption_func(duration)
        if interruption:
            sd.stop()
            break
        else:
            sd.wait()

class Mouth:
    def __init__(self):
        self.model = TextToSpeech(use_deepspeed=True, kv_cache=True, half=True)
        self.sample_rate = 24000
        self.voice_samples, self.conditioning_latents = load_voice('tom')

    @torch.no_grad()
    def say(self, text, listen_interruption_func):
        audio_queue = queue.Queue()
        playback_thread = threading.Thread(target=play_audio_paralell, args=(audio_queue,
                                                                             self.sample_rate,
                                                                             listen_interruption_func))
        playback_thread.start()
        audio_generator = self.model.tts_stream(text,
                                         voice_samples=self.voice_samples,
                                         conditioning_latents=self.conditioning_latents)
        for wav_chunk in audio_generator:
            audio_queue.put(wav_chunk)
            if playback_thread.is_alive() is False:
                playback_thread.join()
                return True
        audio_queue.put(None)
        playback_thread.join()
        return False


    def say_multiple(self, text, listen_interruption_func):
        pattern = r'[.?!]'
        sentences = re.split(pattern, text)
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
        print(sentences)
        for sentence in sentences:
            interruption = self.say(sentence, listen_interruption_func)
            if interruption:
                break


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    mouth = Mouth()

    text = "If there's one thing that makes me nervous about the future of self-driving cars, it's that they'll replace human drivers.\nI think there's a huge opportunity to make human-driven cars safer and more efficient. There's no reason why we can't combine the benefits of self-driving cars with the ease of use of human-driven cars."
    print(text)
    mouth.say(text, lambda x: False)
    sd.wait()
