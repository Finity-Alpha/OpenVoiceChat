# we want to have a single audio handler.
# the audio handler will play audio, record audio, and handle the audio buffer.

import numpy as np


class BaseAudioHandler:
    def __init__(self):
        """
        Setting up the audio handler
        The stream of input and output is set up here.
        """
        self.stream = None
        self.CHUNK = None
        self.RATE = None
        self.vad = None

    def play(self, audio_array, samplerate):
        pass

    def read_input(self) -> bytes:
        """
        Reads a chunk of audio and returns it as a buffer of bytes.
        """
        pass

    def record(self, silence_seconds, vad, logger=None):
        pass

    def wait(self):
        pass
