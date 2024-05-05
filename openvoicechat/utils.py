import threading
import queue

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
