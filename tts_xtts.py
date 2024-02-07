from TTS.api import TTS
import sounddevice as sd
import torch

# Get device



class Mouth:
    def __init__(self, model_id='tts_models/multilingual/multi-dataset/xtts_v2', device='cpu'):
        self.model = TTS(model_id)
        self.device = device
        self.model.to(device)

    def run_tts(self, text):
        output = self.model.tts(text=text,
                                speaker_wav='media/my_voice.wav',
                                language='en')
        return output


    def say(self, text, listen_interruption_func):
        output = self.run_tts(text)
        # get the duration of audio
        duration = len(output) / self.model.config.sampling_rate
        sd.play(output, samplerate=self.model.config.sampling_rate)
        interruption = listen_interruption_func(duration)
        if interruption:
            sd.stop()
            return True
        else:
            sd.wait()
            return False

if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    mouth = Mouth(device=device)

    text = "If there's one thing that makes me nervous about the future of self-driving cars, it's that they'll replace human drivers.\nI think there's a huge opportunity to make human-driven cars safer and more efficient. There's no reason why we can't combine the benefits of self-driving cars with the ease of use of human-driven cars."
    print(text)
    mouth.run_tts(text)
    sd.wait()