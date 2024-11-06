import sounddevice as sd
import re
import queue
import threading
from typing import Callable
import numpy as np
import pysbd
from dotenv import load_dotenv

load_dotenv()


def remove_words_in_brackets_and_spaces(text):
    """
    :param text: input text
    :return: input text with the extra spaces and words in brackets removed. (e.g. [USER])
    """
    pattern = r"\s*\[.*?\]\s*"
    cleaned_text = re.sub(pattern, " ", text)
    cleaned_text = cleaned_text.strip()
    return cleaned_text


class BaseMouth:
    def __init__(self, sample_rate: int, player=sd, wait=True, logger=None):
        """
        Initializes the BaseMouth class.

        :param sample_rate: The sample rate of the audio.
        :param player: The audio player object. Defaults to sounddevice.
        :param wait: Whether to wait for the audio to finish playing. Defaults to True.
        """
        self.sample_rate = sample_rate
        self.interrupted = ""
        self.player = player
        self.seg = pysbd.Segmenter(language="en", clean=True)
        self.wait = wait
        self.logger = logger

    def run_tts(self, text: str) -> np.ndarray:
        """
        :param text: The text to synthesize speech for
        :return: audio numpy array for sounddevice
        """
        raise NotImplementedError("This method should be implemented by the subclass")

    def say_text(self, text: str):
        """
        calls run_tts and plays the audio using the player.
        :param text: The text to synthesize speech for
        """
        output = self.run_tts(text)
        self.player.play(output, samplerate=self.sample_rate)
        self.player.wait()

    def say(self, audio_queue: queue.Queue, listen_interruption_func: Callable):
        """
        Plays the audios in the queue using the player. Stops if interruption occurred.
        :param audio_queue: The queue where the audio is stored for it to be played
        :param listen_interruption_func: callable function from the ear class.
        """
        self.interrupted = ""
        while True:
            output, text = audio_queue.get()
            if output is None:
                self.player.wait()  # wait for the last audio to finish
                break
            # get the duration of audio
            duration = len(output) / self.sample_rate
            self._log_event("playing audio", "TTS", f"{duration} seconds")
            self.player.play(output, samplerate=self.sample_rate)
            interruption = listen_interruption_func(duration)
            if interruption:
                self._log_event("audio interrupted", f"TTS")
                self.player.stop()
                self.interrupted = (interruption, text)
                break
            else:
                if self.wait:
                    self.player.wait()  # No need for wait here

    def say_multiple(self, text: str, listen_interruption_func: Callable):
        """
        Splits the text into sentences. Then plays the sentences one by one
        using run_tts() and say()

        :param text: Input text to synthesize
        :param listen_interruption_func: callable function from the ear class
        """
        sentences = self.seg.segment(text)
        print(sentences)
        audio_queue = queue.Queue()
        say_thread = threading.Thread(
            target=self.say, args=(audio_queue, listen_interruption_func)
        )
        say_thread.start()
        for sentence in sentences:
            output = self.run_tts(sentence)
            audio_queue.put((output, sentence))
            if self.interrupted:
                break
        audio_queue.put((None, ""))
        say_thread.join()

    def _handle_interruption(self, responses_list, interrupt_queue):
        interrupt_transcription, interrupt_text = self.interrupted
        self._log_event("interruption detected", "TTS", interrupt_transcription)
        idx = responses_list.index(interrupt_text)
        assert (
            idx != -1
        ), "Interrupted text not found in responses list. This should not happen. Raise an issue."
        responses_list = responses_list[:idx] + ["..."]
        interrupt_queue.put(interrupt_transcription)
        return responses_list

    def _get_all_text(self, text_queue):
        text = text_queue.get()
        while not text_queue.empty():
            new_text = text_queue.get()
            if new_text is not None:
                text += new_text
            else:
                text_queue.put(None)
                break
        return text

    def _log_event(self, event: str, details: str, further: str = ""):
        if self.logger:
            self.logger.info(
                event, extra={"details": details, "further": f'"{further}"'}
            )

    def say_multiple_stream(
        self,
        text_queue: queue.Queue,
        listen_interruption_func: Callable,
        interrupt_queue: queue.Queue,
        audio_queue: queue.Queue = None,
    ):
        """
        Receives text from the text_queue. As soon as a sentence is made run_tts is called to
        synthesize its speech and sent to the audio_queue for it to be played.

        :param text_queue: The queue where the llm adds the predicted tokens
        :param listen_interruption_func: callable function from the ear class
        :param interrupt_queue: The queue where True is put when interruption occurred.
        :param audio_queue: The queue where the audio to be played is placed

        """
        response = ""
        all_response = []
        interrupt_text_list = []

        if audio_queue is None:
            audio_queue = queue.Queue()
        say_thread = threading.Thread(
            target=self.say, args=(audio_queue, listen_interruption_func)
        )
        self._log_event("audio play thread started", "TTS")
        say_thread.start()
        text = ""

        while text is not None:
            self._log_event("getting all text", "TTS")
            text = self._get_all_text(text_queue)
            self._log_event("all text received", "TTS")

            if text is None:
                self._log_event("Stream ended", "TTS")
                sentence = response
            else:
                response += text
                self._log_event("segmenting text", "TTS", response)
                sentences = self.seg.segment(response)
                # if there are multiple sentences we split and play the first one
                if len(sentences) > 1:
                    self._log_event("multiple sentences detected", "TTS")
                    sentence = sentences[0]
                    response = " ".join([s for s in sentences[1:] if s != "."])
                else:
                    self._log_event("single sentence detected", "TTS")
                    continue

            if sentence.strip() != "":
                self._log_event("cleaning sentence", "TTS")
                clean_sentence = remove_words_in_brackets_and_spaces(sentence).strip()
                if (
                    clean_sentence.strip() != ""
                ):  # sentence only contains words in brackets
                    self._log_event("running tts", "TTS", clean_sentence)
                    output = self.run_tts(clean_sentence)
                    self._log_event("tts output received", "TTS")
                    audio_queue.put((output, clean_sentence))
                    interrupt_text_list.append(clean_sentence)
                all_response.append(sentence)
            # if interruption occurred, handle it
            if self.interrupted:
                all_response = self._handle_interruption(
                    interrupt_text_list, interrupt_queue
                )
                self.interrupted = ""
                break

        audio_queue.put((None, ""))

        say_thread.join()
        self._log_event("audio play thread ended", "TTS")
        if self.interrupted:
            all_response = self._handle_interruption(
                interrupt_text_list, interrupt_queue
            )
        text_queue.queue.clear()
        text_queue.put(" ".join(all_response))
