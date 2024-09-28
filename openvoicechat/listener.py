import numpy as np
import librosa


class BaseListener:
    def __init__(self, samplerate) -> None:
        """
        Initialize the listener
        :param samplerate: int, sample rate of the audio data
        """
        self.sample_rate = samplerate

    def read(self, x):
        """
        Read audio data from the listener
        :param x: int, number of bytes to read, usually ignored
        """
        raise NotImplementedError

    def close(self):
        """
        Close the listener and stop listening
        """
        raise NotImplementedError

    def make_stream(self):
        """
        Start and open the listener
        """
        raise NotImplementedError


class Listener_ws(BaseListener):
    def __init__(self, q, samplerate=44100):
        super().__init__(samplerate)
        self.input_queue = q
        self.listening = False
        self.CHUNK = 5945
        self.RATE = 16_000

    def read(self, x):
        data = self.input_queue.get()
        data = np.frombuffer(data, dtype=np.float32)
        data = librosa.resample(y=data, orig_sr=self.samplerate, target_sr=16_000)
        data = data * (1 << 15)
        data = data.astype(np.int16)
        data = data.tobytes()
        return data

    def close(self):
        self.listening = False

    def make_stream(self):
        self.listening = True
        self.input_queue.queue.clear()
        return self
