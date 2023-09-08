from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torchaudio
import torchaudio.functional as F
import torch
print(); print()



class Ear:
    def __init__(self, model_id='openai/whisper-base.en', device='cpu'):
        self.processor = WhisperProcessor.from_pretrained(model_id)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_id)
        self.device = device
        self.model.to(device)

    @torch.no_grad()
    def listen(self,audio):
        input_features = self.processor(audio, sampling_rate=16_000, return_tensors="pt").input_features.to(self.device) 
        predicted_ids = self.model.generate(input_features)
        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)
        return ' '.join(transcription)
       

if __name__ == "__main__":
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    ear = Ear(device=device)

    audio, sr = torchaudio.load('media/abs.wav')
    audio = F.resample(audio, sr, 16_000)[0]
    text = ear.listen(audio)
    print(text)

