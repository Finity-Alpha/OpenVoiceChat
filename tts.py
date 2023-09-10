from transformers import VitsModel, AutoTokenizer
import sounddevice as sd
import torch
print(); print()

class Mouth:
    def __init__(self, model_id='kakao-enterprise/vits-vctk', speaker_id=0, device='cpu'):
        self.model = VitsModel.from_pretrained(model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.device = device
        self.model.to(device)
        self.speaker_id = speaker_id

    @torch.no_grad()
    def say(self, text):
        inputs = self.tokenizer(text, return_tensors="pt")
        inputs['speaker_id'] = torch.tensor(self.speaker_id)
        inputs = inputs.to(self.device)
        output = self.model(**inputs).waveform[0].to('cpu')
        sd.play(output, samplerate=22050)
        sd.wait()


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    mouth = Mouth(device=device, speaker_id=10)

    text = "Hey, it's Hugging Face on the phone"
    print(text)
    mouth.say(text)
    sd.wait()




