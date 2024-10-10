import threading
import queue
import numpy as np
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TIMING = int(os.environ.get("TIMING", 0))
LOGGING = int(os.environ.get("LOGGING", 0))

timing_path = os.environ.get("TIMING_PATH", "times.csv")


def log_to_file(file_path, text):
    with open(file_path, "a") as file:
        file.write(text + "\n")


def run_chat(
    mouth,
    ear,
    chatbot,
    verbose=True,
    stopping_criteria=lambda x: False,
    starting_message="",
    logging_path="chat_log.txt",
):
    """
    Runs a chat session between a user and a bot.
    The function works by continuously listening to the user's input and generating the bot's responses in separate
    threads. If the user interrupts the bot's speech, the remaining part of the bot's response is saved and prepended
    to the user's next input. The chat stops when the stopping_criteria function returns True for a bot's response.

    :param mouth: A mouth object.
    :param ear: An ear object.
    :param chatbot: A chatbot object.
    :param verbose: If True, prints the user's input and the bot's responses. Defaults to True.
    :param stopping_criteria: A function that determines when the chat should stop. It takes the bot's response as input and returns a boolean. Defaults to a function that always returns False.
    """
    if TIMING:
        pd.DataFrame(columns=["Model", "Time Taken"]).to_csv(timing_path, index=False)

    if starting_message:
        mouth.say_text(starting_message)

    pre_interruption_text = ""
    while True:
        user_input = pre_interruption_text + " " + ear.listen()

        if verbose:
            print("USER: ", user_input)
        if LOGGING:
            log_to_file(logging_path, "USER: " + user_input)

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
        if LOGGING:
            log_to_file(logging_path, "BOT: " + res)
