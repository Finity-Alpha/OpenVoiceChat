import threading
import queue
import librosa
import numpy as np



def run_chat(mouth, ear, chatbot, verbose=True):
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
