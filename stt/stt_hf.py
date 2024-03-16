# from transformers import WhisperProcessor, WhisperForConditionalGeneration
from transformers import pipeline
import torchaudio
import torchaudio.functional as F
import torch
from .base import BaseEar
import numpy as np

print()
print()


class Ear(BaseEar):
    def __init__(self, model_id='openai/whisper-base.en', device='cpu', silence_seconds=2):
        super().__init__(silence_seconds)
        self.pipe = pipeline('automatic-speech-recognition', model=model_id, device=device)
        self.device = device

    @torch.no_grad()
    def transcribe(self, audio):
        transcription = self.pipe(audio)
        return transcription['text'].strip()



if __name__ == "__main__":
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    ear = Ear(device=device)

    audio, sr = torchaudio.load('../media/abs.wav')
    audio = F.resample(audio, sr, 16_000)[0]
    text = ear.transcribe(np.array(audio))
    print(text)

    text = ear.listen()
    print(text)
