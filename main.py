from openvoicechat.tts.tts_xtts import Mouth_xtts
from openvoicechat.llm.llm_ollama import Chatbot_ollama
from openvoicechat.stt.stt_hf import Ear_hf
from openvoicechat.utils import run_chat
from openvoicechat.llm.prompts import llama_sales
import torch
from dotenv import load_dotenv
import os

load_dotenv()


if __name__ == "__main__":
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    print("loading models... ", device)
    load_dotenv()
    ear = Ear_hf(
        model_id="openai/whisper-tiny.en",
        silence_seconds=1.5,
        device=device,
        listen_interruptions=False,
    )

    chatbot = Chatbot_ollama(sys_prompt=llama_sales, model="qwen2:0.5b")

    mouth = Mouth_xtts(device=device)

    run_chat(
        mouth, ear, chatbot, verbose=True, stopping_criteria=lambda x: "[END]" in x
    )
