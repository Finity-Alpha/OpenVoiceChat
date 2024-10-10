import queue
import threading
from openvoicechat.llm.llm_gpt import Chatbot_gpt
from openvoicechat.tts.tts_xtts import Mouth_xtts
import time

chatbot = Chatbot_gpt("You are a helpful assistant")
mouth = Mouth_xtts(device="cuda")

user_input = "Hello, how are you?"

llm_output_queue = queue.Queue()
interrupt_queue = queue.Queue()
llm_thread = threading.Thread(
    target=chatbot.generate_response_stream,
    args=(user_input, llm_output_queue, interrupt_queue),
)
tts_thread = threading.Thread(
    target=mouth.say_multiple_stream,
    args=(llm_output_queue, lambda x: False, interrupt_queue),
)

start = time.monotonic()
llm_thread.start()
tts_thread.start()

llm_thread.join()
tts_thread.join()
end = time.monotonic()

print("Time taken: ", end - start)

if not interrupt_queue.empty():
    pre_interruption_text = interrupt_queue.get()
else:
    pre_interruption_text = ""

res = llm_output_queue.get()
print(res)
