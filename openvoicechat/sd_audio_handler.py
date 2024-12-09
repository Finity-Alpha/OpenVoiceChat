from audio_handler import BaseAudioHandler
import pyaudio
import numpy as np
import queue
from threading import Thread
import time
import sounddevice as sd


class AudioHandler(BaseAudioHandler):
    def __init__(self):
        self.CHUNK = int(1024 * 2)
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.audio_queue = queue.Queue()
        self.is_playing = False
        super().__init__()

    def _play_audio(self):
        while not self.audio_queue.empty():
            audio_array = self.audio_queue.get()
            sd.play(audio_array, samplerate=self.RATE)

    def play(self, audio_array, samplerate):
        self.audio_queue.put(audio_array)
        self.is_playing = True
        play_thread = Thread(target=self._play_audio)
        play_thread.start()

    def wait(self):
        while self.is_playing:
            time.sleep(0.1)

    def record(self, silence_seconds, vad, logger=None):
        frames = []

        # if streamer is None:
        #     stream = make_stream()
        #     global CHUNK
        #     global RATE
        # else:
        #     stream = streamer.make_stream()
        #     CHUNK = streamer.CHUNK
        #     RATE = streamer.RATE
        one_second_iters = int(self.RATE / self.CHUNK)
        if logger:
            logger.info(
                "user recording started",
                extra={
                    "details": "record_user",
                    "further": f"{silence_seconds} seconds",
                },
            )

        while True:
            data = self.read_input()
            assert (
                len(data) == self.CHUNK * 2
            ), "chunk size does not match 2 bytes per sample"
            frames.append(data)
            if len(frames) < one_second_iters * silence_seconds:
                continue
            contains_speech = vad.contains_speech(
                frames[int(-one_second_iters * silence_seconds) :]
            )
            if not started and contains_speech:
                started = True
                if logger:
                    logger.info(
                        "speech detected",
                        extra={"details": "record_user", "further": ""},
                    )
            if started and contains_speech is False:
                break
        # self.stream.close()
        if logger:
            logger.info(
                "user recording ended",
                extra={"details": "record_user", "further": ""},
            )

        # creating a np array from buffer
        frames = np.frombuffer(b"".join(frames), dtype=np.int16)

        # normalization see https://discuss.pytorch.org/t/torchaudio-load-normalization-question/71470
        frames = frames / (1 << 15)

        return frames.astype(np.float32)
