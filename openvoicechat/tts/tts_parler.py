import sounddevice as sd

if __name__ == "__main__":
    from base import BaseMouth
    import torch
else:
    from .base import BaseMouth


"""
It generates high-quality speech with features that can be controlled using a 
simple text prompt (e.g. gender, background noise, speaking rate, pitch and reverberation).

examples:
- A male speaker with a low-pitched voice delivering his words at a fast pace in a small, 
confined space with a very clear audio and an animated tone.
- A female speaker with a slightly low-pitched, quite monotone voice delivers her 
words at a slightly faster-than-average pace in a confined space with very clear audio.
etc ....
"""


class Mouth_parler(BaseMouth):
    def __init__(
        self,
        model_id="parler-tts/parler_tts_mini_v0.1",
        tts_description=None,
        device="cpu",
        temperature=1.0,
        player=sd,
        wait=True,
    ):
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer
        from transformers.modeling_outputs import BaseModelOutput

        if tts_description is None:
            tts_description = (
                "A female speaker with a slightly low-pitched voice delivers her words quite "
                "expressively, in a very confined sounding environment with clear audio quality."
            )
        self.model = ParlerTTSForConditionalGeneration.from_pretrained(model_id).to(
            device
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.device = device
        self.tts_description = tts_description
        input_ids = self.tokenizer(tts_description, return_tensors="pt").input_ids.to(
            device
        )
        self.desc_tensor = BaseModelOutput(
            last_hidden_state=self.model.text_encoder(
                input_ids=input_ids
            ).last_hidden_state
        )
        self.temperature = temperature
        super().__init__(
            sample_rate=self.model.config.sampling_rate, player=player, wait=wait
        )

    def run_tts(self, text):
        prompt_input_ids = self.tokenizer(text, return_tensors="pt").input_ids.to(
            self.device
        )
        generation = self.model.generate(
            encoder_outputs=self.desc_tensor,
            prompt_input_ids=prompt_input_ids,
            temperature=self.temperature,
        )
        audio_arr = generation.cpu().numpy().squeeze()
        return audio_arr


if __name__ == "__main__":

    mouth = Mouth_parler(temperature=1)

    text = (
        "If there's one thing that makes me nervous about the future of self-driving cars, it's that they'll "
        "replace human drivers.\nI think there's a huge opportunity to make human-driven cars safer and more "
        "efficient. There's no reason why we can't combine the benefits of self-driving cars with the ease of use "
        "of human-driven cars."
    )
    print(text)
    mouth.say_multiple(text, lambda x: False)
    sd.wait()
