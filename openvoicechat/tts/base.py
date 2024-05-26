import sounddevice as sd
import re
from time import monotonic
import queue
import threading
from typing import Callable
import numpy as np
import inspect
import asyncio


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
    def __init__(self, sample_rate: int, player=sd):
        self.sample_rate = sample_rate
        self.sentence_stop_pattern = r'[.?](?=\s+\S)'
        self.interrupted = ''
        self.player = player

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
        self.player.play(output, samplerate=self.sample_rate)
        self.player.wait()

    def say(self, audio_queue: queue.Queue, listen_interruption_func: Callable):
        '''
        :param audio_queue: The queue where the audio is stored for it to be played
        :param listen_interruption_func: callable function from the ear class.
        Plays the audios in the queue using sounddevice. Stops if interruption occurred.
        '''
        self.interrupted = ''
        while True:
            output, text = audio_queue.get()
            if output is None:
                break
            # get the duration of audio
            duration = len(output) / self.sample_rate
            self.player.play(output, samplerate=self.sample_rate)
            interruption = listen_interruption_func(duration)
            if interruption:
                self.player.stop()
                self.interrupted = (interruption, text)
                break
            else:
                self.player.wait()

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
            audio_queue.put((output, sentence))
            if self.interrupted:
                break
        audio_queue.put((None, ''))
        say_thread.join()

    def _handle_interruption(self, responses_list, interrupt_queue):
        interrupt_transcription, interrupt_text = self.interrupted
        idx = responses_list.index(interrupt_text)
        assert idx != -1, "Interrupted text not found in responses list. This should not happen. Raise an issue."
        responses_list = responses_list[:idx] + ['...']
        interrupt_queue.put(interrupt_transcription)
        return responses_list

    def say_multiple_stream(self, text_queue: queue.Queue,
                            listen_interruption_func: Callable,
                            interrupt_queue: queue.Queue,
                            audio_queue: queue.Queue = None):
        '''
        :param text_queue: The queue where the llm adds the predicted tokens
        :param listen_interruption_func: callable function from the ear class
        :param interrupt_queue: The queue where True is put when interruption occurred.
        :param audio_queue: The queue where the audio to be played is placed
        Receives text from the text_queue. As soon as a sentence is made run_tts is called to
        synthesize its speech.
        '''
        response = ''
        all_response = []
        interrupt_text_list = []
        if audio_queue is None:
            audio_queue = queue.Queue()
        say_thread = threading.Thread(target=self.say, args=(audio_queue, listen_interruption_func))
        say_thread.start()
        while True:
            text = text_queue.get()
            if text is None:
                sentence = response
            else:
                response += text
                if bool(re.search(self.sentence_stop_pattern, response)):
                    sentences = re.split(self.sentence_stop_pattern, response, maxsplit=1)
                    sentence = sentences[0]
                    response = sentences[1]
                else:
                    continue
            if sentence.strip() == '':
                break
            clean_sentence = remove_words_in_brackets_and_spaces(sentence).strip()
            output = self.run_tts(clean_sentence)
            audio_queue.put((output, clean_sentence))
            all_response.append(sentence)
            interrupt_text_list.append(clean_sentence)
            if self.interrupted:
                all_response = self._handle_interruption(interrupt_text_list, interrupt_queue)
                self.interrupted = ''
                break
            if text is None:
                break
        audio_queue.put((None, ''))
        say_thread.join()
        if self.interrupted:
            all_response = self._handle_interruption(interrupt_text_list, interrupt_queue)
        text_queue.queue.clear()
        text_queue.put('. '.join(all_response))
