import threading
import queue
from dotenv import load_dotenv

load_dotenv()


def run_chat(
    mouth,
    ear,
    chatbot,
    verbose=True,
    stopping_criteria=lambda x: False,
    starting_message="",
):
    """
    Runs a chat session between a user and a bot.
    The function works by continuously listening to the user's input and generating the bot's responses in separate
    threads. If the user interrupts the bot's speech, the remaining part of the bot's response is saved and prepended
    to the user's next input. The chat stops when the stopping_criteria function returns True for a bot's response.

    :param mouth: A mouth object.
    :param ear: An ear object.
    :param chatbot: A chatbot object.
    :param stopping_criteria: A function that determines when the chat should stop. It takes the bot's response as input and returns a boolean. Defaults to a function that always returns False.
    """

    if starting_message:
        mouth.say_text(starting_message)

    pre_interruption_text = ""
    while True:
        user_input = pre_interruption_text + " " + ear.listen()

        if verbose:
            print("USER: ", user_input)

        llm_output_queue = queue.Queue()
        interrupt_queue = queue.Queue()
        llm_thread = threading.Thread(
            target=chatbot.generate_response_stream,
            args=(user_input, llm_output_queue, interrupt_queue),
        )
        tts_thread = threading.Thread(
            target=mouth.say_multiple_stream,
            args=(llm_output_queue, ear.interrupt_listen, interrupt_queue),
        )

        llm_thread.start()
        tts_thread.start()

        llm_thread.join()
        tts_thread.join()
        if not interrupt_queue.empty():
            pre_interruption_text = interrupt_queue.get()
        else:
            pre_interruption_text = ""

        res = llm_output_queue.get()
        if stopping_criteria(res):
            break
        if verbose:
            print("BOT: ", res)
