import threading
import queue
import librosa
import numpy as np



def run_chat(mouth, ear, chatbot, verbose=True,
             stopping_criteria=lambda x: False):
    """
    Runs a chat session between a user and a bot.

    Parameters: mouth (object): An object responsible for the bot's speech output. ear (object): An object
    responsible for listening to the user's input. chatbot (object): An object responsible for generating the bot's
    responses. verbose (bool, optional): If True, prints the user's input and the bot's responses. Defaults to True.
    stopping_criteria (function, optional): A function that determines when the chat should stop. It takes the bot's
    response as input and returns a boolean. Defaults to a function that always returns False.

    The function works by continuously listening to the user's input and generating the bot's responses in separate
    threads. If the user interrupts the bot's speech, the remaining part of the bot's response is saved and prepended
    to the user's next input. The chat stops when the stopping_criteria function returns True for a bot's response.
    """
    pre_interruption_text = ''
    while True:
        user_input = pre_interruption_text + ' ' + ear.listen()
        if verbose:
            print("USER: ", user_input)

        llm_output_queue = queue.Queue()
        interrupt_queue = queue.Queue()
        llm_thread = threading.Thread(target=chatbot.generate_response_stream,
                                      args=(user_input, llm_output_queue, interrupt_queue))
        tts_thread = threading.Thread(target=mouth.say_multiple_stream,
                                      args=(llm_output_queue, ear.interrupt_listen, interrupt_queue))

        llm_thread.start()
        tts_thread.start()

        tts_thread.join()
        llm_thread.join()
        if not interrupt_queue.empty():
            pre_interruption_text = interrupt_queue.get()

        res = llm_output_queue.get()
        if stopping_criteria(res):
            break
        if verbose:
            print('BOT: ', res)


class Player_ws:
    def __init__(self, q):
        self.output_queue = q
        self.playing = False

    def play(self, audio_array, samplerate):
        audio_array = audio_array / (1 << 15)
        audio_array = audio_array.astype(np.float32)
        audio_array = librosa.resample(y=audio_array, orig_sr=samplerate, target_sr=44100)
        audio_array = audio_array.tobytes()
        self.output_queue.put(audio_array)

    def stop(self):
        self.playing = False
        self.output_queue.queue.clear()
        self.output_queue.put('stop'.encode())

    def wait(self):
        time_to_wait = 0
        # while not self.output_queue.empty():
        #     time.sleep(0.1)
        #     peek at the first element
        # time_to_wait = len(self.output_queue.queue[0]) / (44100 * 4)
        # print(time_to_wait)
        # time.sleep(time_to_wait)
        self.playing = False


class Listener_ws:
    def __init__(self, q):
        self.input_queue = q
        self.listening = False
        self.CHUNK = 5945
        self.RATE = 16_000

    def read(self, x):
        data = self.input_queue.get()
        data = np.frombuffer(data, dtype=np.float32)
        data = librosa.resample(y=data, orig_sr=44100, target_sr=16_000)
        data = data * (1 << 15)
        data = data.astype(np.int16)
        data = data.tobytes()
        return data

    def close(self):
        pass

    def make_stream(self):
        self.listening = True
        self.input_queue.queue.clear()
        return self
