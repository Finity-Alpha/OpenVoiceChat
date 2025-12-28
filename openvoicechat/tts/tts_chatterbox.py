import torchaudio as ta
import torch
from chatterbox.tts_turbo import ChatterboxTurboTTS
if __name__ == "__main__":
    from .base import BaseMouth
else:
    from .base import BaseMouth
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
load_dotenv()

class mouth_ChatterBox(BaseMouth):
    def __init__(
        self,
        device="cuda",
        speaker=None,
        wait=True,
        player=sd,
        logger=None,
    ):
        self.device = device
        self.model = ChatterboxTurboTTS.from_pretrained(device=self.device)

    def run_tts(self,text,audio_prompt_path):
        return self.model.generate(text,audio_prompt_path=audio_prompt_path)
        
if __name__ == "__main__":
    tts = mouth_ChatterBox(device="cuda")
    text = "Hi there, John here from MochaFone calling you back [chuckle], have you got one minute to chat about the billing issue?"
    wav = tts.run_tts(text, audio_prompt_path="data/refs/harvard.wav")
    ta.save("test-turbo.wav", wav, tts.model.sr)

