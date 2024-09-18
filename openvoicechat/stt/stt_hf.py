if __name__ == "__main__":
    import torch
    from base import BaseEar
else:
    from .base import BaseEar
import numpy as np


class Ear_hf(BaseEar):
    def __init__(
        self,
        model_id="openai/whisper-base.en",
        device="cpu",
        silence_seconds=2,
        generate_kwargs=None,
        listener=None,
        listen_interruptions=True,
    ):
        super().__init__(
            silence_seconds,
            listener=listener,
            listen_interruptions=listen_interruptions,
        )
        from transformers import pipeline

        self.pipe = pipeline(
            "automatic-speech-recognition", model=model_id, device=device
        )
        self.device = device
        self.generate_kwargs = generate_kwargs

    def transcribe(self, audio):
        from torch import no_grad

        with no_grad():
            transcription = self.pipe(audio, generate_kwargs=self.generate_kwargs)
        return transcription["text"].strip()


if __name__ == "__main__":
    import torchaudio
    import torchaudio.functional as F

    device = "cuda" if torch.cuda.is_available() else "cpu"

    ear = Ear_hf(device=device)

    audio, sr = torchaudio.load("../media/abs.wav")
    audio = F.resample(audio, sr, 16_000)[0]
    text = ear.transcribe(np.array(audio))
    print(text)

    text = ear.listen()
    print(text)
