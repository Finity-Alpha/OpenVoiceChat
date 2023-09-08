from transformers import VitsModel, AutoTokenizer
import sounddevice as sd
import torch
print(); print()

class Mouth:
    def __init__(self, model_id='Matthijs/vits-vctk', speaker_id=0, device='cpu'):
        self.model = VitsModel.from_pretrained(model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.device = device
        self.model.to(device)
        self.speaker_id = speaker_id
    
    def say(self, text):
        inputs = self.tokenizer(text, return_tensors="pt")
        inputs['speaker_id'] = torch.tensor(3)
        inputs.to(self.device)
        with torch.no_grad():
            output = self.model(**inputs).waveform[0].to('cpu')
        sd.play(output, samplerate=22050)


if __name__ == '__main__':
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    mouth = Mouth(device=device)

    text = "Hey, it's Hugging Face on the phone"
    print(text)
    mouth.say(text)
    sd.wait()




