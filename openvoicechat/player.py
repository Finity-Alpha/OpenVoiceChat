import numpy as np
import librosa
import multiprocessing
import time


class BasePlayer:
    def __init__(self):
        """
        Initialize the player
        """

    def play(self, audio_array, samplerate):
        """
        Play audio data
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


class Player_ws:
    def __init__(self, q):
        super().__init__()
        self.output_queue = q
        self.playing = False
        self._timer_thread = None

    def play(self, audio_array, samplerate):
        self.playing = True
        duration = len(audio_array) / samplerate
        if audio_array.dtype == np.int16:
            audio_array = audio_array / (1 << 15)
        audio_array = audio_array.astype(np.float32)
        audio_array = librosa.resample(
            y=audio_array, orig_sr=samplerate, target_sr=44100
        )
        audio_array = audio_array.tobytes()
        self.output_queue.put(audio_array)
        # the timer thread is used to wait for the audio to finish playing on the server-side
        if self._timer_thread is not None:
            if self._timer_thread.is_alive():
                self._timer_thread.terminate()
        self._timer_thread = multiprocessing.Process(
            target=time.sleep, args=(duration,)
        )
        self._timer_thread.start()

    def stop(self):
        self.playing = False
        self.output_queue.queue.clear()
        self.output_queue.put("stop".encode())
        self._timer_thread.terminate()

    def wait(self):
        self._timer_thread.join()
        self.playing = False
