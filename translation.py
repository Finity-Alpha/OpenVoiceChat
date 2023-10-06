import torch
from seamless_communication.models.inference import Translator
from utils import record
import sounddevice as sd



translator = Translator("seamlessM4T_large", vocoder_name_or_card="vocoder_36langs", device=torch.device("cuda:0"))

audio = record(3)
audio = torch.tensor(audio).unsqueeze(1) #idk why but this is the shape
translated_text, wav, sr = translator.predict(audio, "s2st", 'urd')
sd.play(wav.cpu().numpy()[0][0], sr)
sd.wait()
print(translated_text)




