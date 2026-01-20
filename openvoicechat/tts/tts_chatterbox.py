import torchaudio as ta
import torch
from chatterbox.tts_turbo import ChatterboxTurboTTS
import sys
from pathlib import Path
try:
    from .base import BaseMouth
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from base import BaseMouth

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
        self.model.prepare_conditionals("data/refs/harvard.wav")

    def run_tts(self, text, audio_prompt_path=None):
        wav_tensor = self.model.generate(text)
        # Ensure wav_tensor is 2D (channels, samples)
        if wav_tensor.dim() == 1:
            wav_tensor = wav_tensor.unsqueeze(0)
        # Convert to numpy array and transpose to (samples, channels) for sounddevice
        wav_np = wav_tensor.cpu().numpy().T
        return wav_np
    
if __name__ == "__main__":
    tts = mouth_ChatterBox(device="cuda")
    text = "Hi there, John here from MochaFone calling you back [chuckle], have you got one minute to chat about the billing issue?"
    wav = tts.run_tts(text)
    ta.save("test-turbo.wav", torch.from_numpy(wav.T), tts.model.sr)

