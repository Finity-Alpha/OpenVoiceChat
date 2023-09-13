from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torchaudio
import torchaudio.functional as F
import torch
import numpy as np
import pyaudio
import audioop
print(); print()



class Ear:
    def __init__(self, model_id='openai/whisper-base.en', device='cpu', silence_seconds=1):
        self.processor = WhisperProcessor.from_pretrained(model_id)
        self.model = WhisperForConditionalGeneration.from_pretrained(model_id)
        self.device = device
        self.model.to(device)
        self.silence_seconds = silence_seconds

    @torch.no_grad()
    def transcribe(self, audio):
        input_features = self.processor(audio, sampling_rate=16_000, return_tensors="pt").input_features.to(self.device) 
        predicted_ids = self.model.generate(input_features)
        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)
        return ' '.join(transcription)
    
    def record(self):
        seconds_silence = self.silence_seconds #changing this might make the convo more natural
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1 #make sure this is 1
        RATE = 16000
        RECORD_SECONDS = 100
        WAVE_OUTPUT_FILENAME = "user.wav"

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("* recording")

        frames = []

        started = False
        one_second_iters = int(RATE/CHUNK)
        silent_iters = 0

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
            rms = audioop.rms(data, p.get_sample_size(FORMAT))
            decibel = 20 * np.log10(rms)
            if not started and decibel > 50:
                started = True

            if started and decibel < 50:
                silent_iters += 1

            if started and decibel > 50:
                silent_iters = 0

            if silent_iters >= one_second_iters*seconds_silence:
                break
        
        print("* done recording")
        
        #creating a np array from buffer
        frames = np.frombuffer(b''.join(frames), dtype=np.int16)
        
        #normalization see https://discuss.pytorch.org/t/torchaudio-load-normalization-question/71470
        frames = frames / (1 << 15)
        
        return frames.astype(np.float32)
    
    def listen(self):
        audio = self.record()
        text = self.transcribe(audio)
        return text
       

if __name__ == "__main__":
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    ear = Ear(device=device)

    audio, sr = torchaudio.load('media/abs.wav')
    audio = F.resample(audio, sr, 16_000)[0]
    text = ear.transcribe(audio)
    print(text)

    text = ear.listen()
    print(text)

