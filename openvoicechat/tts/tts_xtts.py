import sounddevice as sd
import numpy as np

if __name__ == "__main__":
    from base import BaseMouth
else:
    from .base import BaseMouth


class Mouth_xtts(BaseMouth):
    def __init__(
        self,
        model_id="tts_models/en/jenny/jenny",
        device="cpu",
        player=sd,
        speaker=None,
        wait=True,
    ):
        from TTS.api import TTS

        self.model = TTS(model_id)
        self.device = device
        self.model.to(device)
        self.speaker = speaker
        super().__init__(
            sample_rate=self.model.synthesizer.output_sample_rate,
            player=player,
            wait=wait,
        )

    def run_tts(self, text):
        output = self.model.tts(
            text=text,
            split_sentences=False,
            speaker=self.speaker,
            language="en" if self.model.is_multi_lingual else None,
        )
        return np.array(output)


if __name__ == "__main__":
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    mouth = Mouth_xtts(device=device)

    text = (
        "If there's one thing that makes me nervous about the future of self-driving cars, it's that they'll "
        "replace human drivers.\nI think there's a huge opportunity to make human-driven cars safer and more "
        "efficient. There's no reason why we can't combine the benefits of self-driving cars with the ease of use "
        "of human-driven cars."
    )
    print(text)
    mouth.say_multiple(text, lambda x: False)
    sd.wait()
