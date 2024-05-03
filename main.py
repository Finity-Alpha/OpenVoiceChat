from openvoicechat.tts.tts_piper import Mouth_piper as Mouth
from openvoicechat.llm.llm_gpt import Chatbot_gpt as Chatbot
from openvoicechat.stt.stt_hf import Ear_hf as Ear
import torch
from openvoicechat.prompts import llama_sales
import torchaudio
import torchaudio.functional as F
import numpy as np
import threading
import queue

if __name__ == "__main__":
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print('loading models... ', device)

    ear = Ear(silence_seconds=2, device=device)
    audio, sr = torchaudio.load('media/my_voice.wav')
    audio = F.resample(audio, sr, 16_000)[0]
    # ear.transcribe(np.array(audio))

    john = Chatbot(sys_prompt=llama_sales)

    mouth = Mouth(device=device)
    mouth.say_text('Good morning!')

    print("type: exit, quit or stop to end the chat")
    print("Chat started:")
    pre_interruption_text = ''
    while True:
        user_input = pre_interruption_text + ' ' + ear.listen()
        if user_input.lower() in ["exit", "quit", "stop"]:
            break
        print(user_input)

        llm_output_queue = queue.Queue()
        interrupt_queue = queue.Queue()
        llm_thread = threading.Thread(target=john.generate_response_stream,
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
        print('res ', res)
        if '[END]' in res:
            break
