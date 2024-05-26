import torch
from .utils import record_user, record_interruption, record_user_stream
from .vad import VoiceActivityDetection
import re
from time import monotonic
import numpy as np
from threading import Thread
from queue import Queue

class BaseEar:
    def __init__(self, silence_seconds=3,
                 not_interrupt_words=None,
                 listener=None):
        if not_interrupt_words is None:
            not_interrupt_words = ['you', 'yes', 'yeah', 'hmm']  # you because whisper says "you" in silence
        self.silence_seconds = silence_seconds
        self.not_interrupt_words = not_interrupt_words
        self.vad = VoiceActivityDetection()
        self.listener = listener

    @torch.no_grad()
    def transcribe(self, input: np.ndarray) -> str:
        '''
        :param input: fp32 numpy array of the audio
        :return: transcription
        '''
        raise NotImplementedError("This method should be implemented by the subclass")

    def transcribe_stream(self, audio_queue: Queue, transcription_queue: Queue):
        '''
        :param audio_queue: Queue containing audio chunks from pyaudio stream
        :param transcription_queue: Queue to put transcriptions
        '''
        raise NotImplementedError("This method should be implemented by the subclass")

    def listen(self) -> str:
        '''
        :return: transcription
        records audio using record_user and returns its transcription
        '''
        audio = record_user(self.silence_seconds, self.vad, self.listener)
        text = self.transcribe(audio)
        return text

    def listen_stream(self) -> str:
        '''
        :return: transcription
        records audio using record_user and returns its transcription
        '''
        audio_queue = Queue()
        transcription_queue = Queue()

        audio_thread = Thread(target=record_user_stream, args=(self.silence_seconds, self.vad, audio_queue))
        transcription_thread = Thread(target=self.transcribe_stream, args=(audio_queue, transcription_queue))

        audio_thread.start()
        transcription_thread.start()

        audio_thread.join()
        transcription_thread.join()

        text = ''
        while True:
            _ = transcription_queue.get()
            if _ is None:
                break
            text += _ + ' '
        return text

    def listen_timing(self):
        audio = record_user(self.silence_seconds, self.vad)
        start = monotonic()
        text = self.transcribe(audio)
        end = monotonic()
        return text, end - start

    def interrupt_listen(self, record_seconds=100) -> str:
        '''
        :param record_seconds: Max seconds to record for
        :return: boolean indicating the if an interruption occured
        Records audio with interruption. Transcribes audio if
        voice activity detected and returns True if transcription indicates
        interruption.
        '''
        while record_seconds > 0:
            interruption_audio = record_interruption(self.vad, record_seconds, streamer=self.listener)
            # duration of interruption audio
            if interruption_audio is None:
                return ''
            else:
                duration = len(interruption_audio) / 16_000
                text = self.transcribe(interruption_audio)
                # remove any punctuation using re
                text = re.sub(r'[^\w\s]', '', text)
                text = text.lower()
                text = text.strip()
                if text in self.not_interrupt_words:
                    record_seconds -= duration
                else:
                    return text
