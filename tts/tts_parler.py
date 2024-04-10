import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf
from tts.base import BaseMouth

'''
It generates high-quality speech with features that can be controlled using a 
simple text prompt (e.g. gender, background noise, speaking rate, pitch and reverberation).

examples:
- A male speaker with a low-pitched voice delivering his words at a fast pace in a small, 
confined space with a very clear audio and an animated tone.
- A female speaker with a slightly low-pitched, quite monotone voice delivers her 
words at a slightly faster-than-average pace in a confined space with very clear audio.
etc ....
'''

class Mouth_parler(BaseMouth):
    def __init__(self, model_id='parler-tts/parler_tts_mini_v0.1', tts_description='A female speaker with a slightly low-pitched voice delivers her words quite expressively, in a very confined sounding environment with clear audio quality.', device='cuda:0' if torch.cuda.is_available() else 'cpu'):
        self.model = ParlerTTSForConditionalGeneration.from_pretrained(model_id).to(device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.device = device
        self.tts_description = tts_description
        super().__init__(sample_rate=self.model.config.sampling_rate)

    def run_tts(self, text):
        input_ids = self.tokenizer(self.tts_description, return_tensors="pt").input_ids.to(self.device)
        prompt_input_ids = self.tokenizer(text, return_tensors="pt").input_ids.to(self.device)
        generation = self.model.generate(input_ids=input_ids, prompt_input_ids=prompt_input_ids)
        audio_arr = generation.cpu().numpy().squeeze()
        return audio_arr