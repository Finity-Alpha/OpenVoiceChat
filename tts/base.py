import sounddevice as sd
import torch
import re
from time import monotonic


class BaseMouth:
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate

    @torch.no_grad()
    def run_tts(self, text):
        raise NotImplementedError('This method should be implemented by the subclass')

    def say(self, text, listen_interruption_func):
        output = self.run_tts(text)
        # get the duration of audio
        duration = len(output) / self.sample_rate
        sd.play(output, samplerate=self.sample_rate)
        interruption = listen_interruption_func(duration)
        if interruption:
            sd.stop()
            return True
        else:
            sd.wait()
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

    def say_timing(self, text, listen_interruption_func):
        start = monotonic()
        output = self.run_tts(text)
        end = monotonic()
        # get the duration of audio
        duration = len(output) / self.sample_rate
        sd.play(output, samplerate=self.sample_rate)
        interruption = listen_interruption_func(duration)
        if interruption:
            sd.stop()
            return True, end - start
        else:
            sd.wait()
            return False, end - start

    def say_multiple_timing(self, text, listen_interruption_func):
        pattern = r'[.?!]'
        sentences = re.split(pattern, text)
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
        print(sentences)
        time_taken = None
        for sentence in sentences:
            interruption, tt = self.say_timing(sentence, listen_interruption_func)
            if time_taken is None:
                time_taken = tt
            if interruption:
                break
        return time_taken
