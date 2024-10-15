# install using pip install git+https://github.com/myshell-ai/MeloTTS.git
# see https://github.com/myshell-ai/MeloTTS/blob/main/docs/install.md
import sounddevice as sd
import numpy as np

if __name__ == "__main__":
    from base import BaseMouth
else:
    from .base import BaseMouth


class Mouth_melo(BaseMouth):
    def __init__(
        self,
        language="EN",
        device="cpu",
        speed=1.2,
        player=sd,
        speaker="EN-US",
    ):
        from melo.api import TTS

        self.speed = speed
        self.speaker = speaker

        self.model = TTS(language=language, device=device)
        self.speaker_ids = self.model.hps.data.spk2id

        super().__init__(sample_rate=44100, player=player)

    def run_tts(self, text):
        if self.speaker in self.speaker_ids:
            speaker_id = self.speaker_ids[self.speaker]
        else:
            speaker_id = self.speaker_ids["EN-US"]
        output = self.model.tts_to_file(text, speaker_id, None, speed=self.speed)
        return np.array(output)


if __name__ == "__main__":
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    mouth = Mouth_melo(device=device)

    text = (
        "If there's one thing that makes me nervous about the future of self-driving cars, it's that they'll "
        "replace human drivers.\nI think there's a huge opportunity to make human-driven cars safer and more "
        "efficient. There's no reason why we can't combine the benefits of self-driving cars with the ease of use "
        "of human-driven cars."
    )
    print(text)
    mouth.say_multiple(text, lambda x: False)
    sd.wait()
