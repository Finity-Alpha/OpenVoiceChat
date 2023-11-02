from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torchaudio
import torchaudio.functional as F
import torch
from utils import record
print(); print()



class Ear:
    def __init__(self, model_id='openai/whisper-base.en', device='cpu', silence_seconds=2):
        self.processor = WhisperProcessor.from_pretrained(model_id)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_id)
        self.device = device
        self.model.to(device)
        self.silence_seconds = silence_seconds

    @torch.no_grad()
    def transcribe(self, audio):
        input_features = self.processor(audio, sampling_rate=16_000, return_tensors="pt").input_features.to(self.device) 
        predicted_ids = self.model.generate(input_features)
        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)
        return ' '.join(transcription)
    

    def listen(self):
        audio = record(self.silence_seconds)
        text = self.transcribe(audio)
        return text
       

if __name__ == "__main__":
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    ear = Ear(device=device)

    audio, sr = torchaudio.load('media/abs.wav')
    audio = F.resample(audio, sr, 16_000)[0]
    text = ear.transcribe(audio)
    print(text)

    text = ear.listen()
    print(text)

