import sounddevice as sd
import torch
import re
from time import monotonic
import queue
import threading
from typing import Callable
import numpy as np


def remove_words_in_brackets_and_spaces(text):
    '''
    :param text: input text
    :return: input text with the extra spaces and words in brackets removed. (e.g. [USER])
    '''
    pattern = r'\s*\[.*?\]\s*'
    cleaned_text = re.sub(pattern, ' ', text)
    cleaned_text = cleaned_text.strip()
    return cleaned_text


class BaseMouth:
    def __init__(self, sample_rate: int):
        self.sample_rate = sample_rate
        self.sentence_stop_pattern = r'[.?](?=\s+\S)'
        self.interrupted = ''

    @torch.no_grad()
    def run_tts(self, text: str) -> np.ndarray:
        '''
        :param text: The text to synthesize speech for
        :return: audio numpy array for sounddevice
        '''
        raise NotImplementedError('This method should be implemented by the subclass')

    def say_text(self, text: str):
        '''
        :param text: The text to synthesize speech for
        calls run_tts and plays the audio using sounddevice.
        '''
        output = self.run_tts(text)
        sd.play(output, samplerate=self.sample_rate)
        sd.wait()

    def say(self, audio_queue: queue.Queue, listen_interruption_func: Callable):
        '''
        :param audio_queue: The queue where the audio is stored for it to be played
        :param listen_interruption_func: callable function from the ear class.
        Plays the audios in the queue using sounddevice. Stops if interruption occurred.
        '''
        self.interrupted = ''
        while True:
            output = audio_queue.get()
            if output is None:
                break
            # get the duration of audio
            duration = len(output) / self.sample_rate
            sd.play(output, samplerate=self.sample_rate)
            interruption = listen_interruption_func(duration)
            if interruption:
                sd.stop()
                self.interrupted = interruption
                break
            else:
                sd.wait()

    def say_multiple(self, text: str, listen_interruption_func: Callable):
        '''
        :param text: Intput text to synthesize
        :param listen_interruption_func: callable function from the ear class
        Splits the text into sentences separated by ['.', '?', '!']. Then plays the sentences one by one
        using run_tts and say
        '''
        pattern = r'[.?!]'
        sentences = re.split(pattern, text)
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
        print(sentences)
        audio_queue = queue.Queue()
        say_thread = threading.Thread(target=self.say, args=(audio_queue, listen_interruption_func))
        say_thread.start()
        for sentence in sentences:
            output = self.run_tts(sentence)
            audio_queue.put(output)
            if self.interrupted:
                break
        audio_queue.put(None)
        say_thread.join()

    def say_multiple_stream(self, text_queue: queue.Queue,
                            listen_interruption_func: Callable, interrupt_queue: queue.Queue):
        '''
        :param text_queue: The queue where the llm adds the predicted tokens
        :param listen_interruption_func: callable function from the ear class
        :param interrupt_queue: The queue where True is put when interruption occurred.
        Receives text from the text_queue. As soon as a sentence is made run_tts is called to
        synthesize its speech.
        '''
        response = ''
        all_response = ''
        audio_queue = queue.Queue()
        say_thread = threading.Thread(target=self.say, args=(audio_queue, listen_interruption_func))
        say_thread.start()
        while True:
            text = text_queue.get()
            if text is None:
                response = remove_words_in_brackets_and_spaces(response).strip()
                if response.strip() != '':
                    output = self.run_tts(response)
                    audio_queue.put(output)
                if self.interrupted:
                    interrupt_queue.put(self.interrupted)
                    all_response += ' ...'
                text_queue.put(all_response)
                break
            response += text
            all_response += text
            if bool(re.search(self.sentence_stop_pattern, response)):
                sentences = re.split(self.sentence_stop_pattern, response, maxsplit=1)
                sentence = sentences[0]
                response = sentences[1]
                sentence = remove_words_in_brackets_and_spaces(sentence).strip()
                output = self.run_tts(sentence)
                audio_queue.put(output)
                if self.interrupted:
                    text_queue.put(all_response + ' ...')
                    interrupt_queue.put(self.interrupted)
                    break
        audio_queue.put(None)
        say_thread.join()
        if self.interrupted:
            interrupt_queue.put(self.interrupted)

