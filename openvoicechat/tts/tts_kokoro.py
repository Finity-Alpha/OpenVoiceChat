import sounddevice as sd
import torch
import soundfile as sf
from kokoro import KPipeline

if __name__ == "__main__":
    from base import BaseMouth
else:
    from .base import BaseMouth


class Mouth_kokoro(BaseMouth):
    def __init__(
        self,
        lang_code="a",  # 'a' for American English, 'b' for British English
        voice="af_heart",
        speed=1.0,
        device="cpu",
        player=sd,
        wait=True,
        logger=None,
    ):
        self.pipeline = KPipeline(lang_code=lang_code)
        self.voice = voice
        self.speed = speed
        self.device = device
        # Kokoro uses 24kHz sample rate
        super().__init__(sample_rate=24000, player=player, wait=wait, logger=logger)

    def run_tts(self, text):
        with torch.no_grad():
            # Generate audio using kokoro pipeline
            generator = self.pipeline(
                text, voice=self.voice, speed=self.speed, split_pattern=r"\n+"
            )

            # Collect all audio segments
            audio_segments = []
            for i, (gs, ps, audio) in enumerate(generator):
                audio_segments.append(audio)

            # Concatenate all segments if multiple
            if len(audio_segments) == 1:
                return audio_segments[0]
            else:
                import numpy as np

                return np.concatenate(audio_segments)


if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    mouth = Mouth_kokoro(
        lang_code="a",  # American English
        voice="af_heart",
        speed=1.0,
        device=device,
    )

    text = (
        "If there's one thing that makes me nervous about the future of self-driving cars, it's that they'll "
        "replace human drivers.\nI think there's a huge opportunity to make human-driven cars safer and more "
        "efficient. There's no reason why we can't combine the benefits of self-driving cars with the ease of use "
        "of human-driven cars."
    )
    print(text)
    mouth.say_multiple(text, lambda x: False)
    sd.wait()
