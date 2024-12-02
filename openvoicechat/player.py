import numpy as np
import librosa
import multiprocessing
import time
import queue
import json
import sounddevice as sd  # maybe should be in another file


class BasePlayer:
    def __init__(self):
        """
        Initialize the player, responsible for initializing the audio device, the audio buffer etc.
        """

    def play(self, audio_array, samplerate):
        """
        Push the audio data to the audio buffer
        :param audio_array: numpy array, audio data to be played
        :param samplerate: int, sample rate of the audio data
        """
        raise NotImplementedError

    def stop(self):
        """
        Stop playing audio
        """
        raise NotImplementedError

    def wait(self):
        """
        Wait for the audio to finish playing
        """
        raise NotImplementedError


class Player_sd(BasePlayer):
    def play_thread(self):
        sd.default.samplerate = self.target_sr
        while True:
            if self.playing:
                audio_array = self.audio_buffer.get()
                if audio_array == "stop":
                    sd.stop()
                    break
                sd.play(audio_array)

    def __init__(self):
        self.audio_buffer = queue.Queue()
        self.playing = False

    def play(self, audio_array, samplerate):
        self.playing = True
        self.audio_buffer.put(audio_array)

    def stop(self):
        self.playing = False
        self.audio_buffer.put("stop")


class Player_ws:
    def __init__(self, output_queue: queue.Queue):
        super().__init__()
        self.playing = False
        self.target_sr = 44100
        self.output_queue = output_queue

    def play(self, audio_array, samplerate):
        self.playing = True
        if audio_array.dtype == np.int16:
            audio_array = audio_array / (1 << 15)
        audio_array = audio_array.astype(np.float32)
        audio_array = librosa.resample(
            y=audio_array, orig_sr=samplerate, target_sr=self.target_sr
        )
        audio_array_json = {
            "type": "tts",
            "data": audio_array.tolist(),  # Convert numpy array to list for JSON serialization
        }
        self.output_queue.put(json.dumps(audio_array_json).encode())

    def stop(self):
        self.playing = False
        response = {"type": "action", "data": "stop"}
        self.output_queue.put(json.dumps(response).encode())

    def wait(self):
        response = {"type": "action", "data": "wait"}
        self.output_queue.put(json.dumps(response).encode())
        while self.playing:
            time.sleep(0.05)
            pass

    def handle_message(self, message):
        if message == "stopped" or message == "waited":
            self.playing = False
