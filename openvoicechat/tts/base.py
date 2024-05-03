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
            output, text = audio_queue.get()
            if output is None:
                break
            # get the duration of audio
            duration = len(output) / self.sample_rate
            sd.play(output, samplerate=self.sample_rate)
            interruption = listen_interruption_func(duration)
            if interruption:
                sd.stop()
                self.interrupted = (interruption, text)
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
                            listen_interruption_func: Callable, interrupt_queue: queue.Queue):
        '''
        :param text_queue: The queue where the llm adds the predicted tokens
        :param listen_interruption_func: callable function from the ear class
        :param interrupt_queue: The queue where True is put when interruption occurred.
        Receives text from the text_queue. As soon as a sentence is made run_tts is called to
        synthesize its speech.
        '''
        response = ''
        all_response = []
        audio_queue = queue.Queue()
        say_thread = threading.Thread(target=self.say, args=(audio_queue, listen_interruption_func))
        say_thread.start()
        while True:
            text = text_queue.get()
            if text is None:
                sentence = remove_words_in_brackets_and_spaces(response).strip()
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
            sentence = remove_words_in_brackets_and_spaces(sentence).strip()
            output = self.run_tts(sentence)
            audio_queue.put((output, sentence))
            all_response.append(sentence)
            if self.interrupted:
                all_response = self._handle_interruption(all_response, interrupt_queue)
                self.interrupted = ''
                break
            if text is None:
                break
        audio_queue.put((None, ''))
        say_thread.join()
        if self.interrupted:
            all_response = self._handle_interruption(all_response, interrupt_queue)
        text_queue.queue.clear()
        text_queue.put('. '.join(all_response))

