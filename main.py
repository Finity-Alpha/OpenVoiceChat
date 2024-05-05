from openvoicechat.tts.tts_piper import Mouth_piper as Mouth
from openvoicechat.llm.llm_gpt import Chatbot_gpt as Chatbot
from openvoicechat.stt.stt_hf import Ear_hf as Ear
from openvoicechat.utils import run_chat
from openvoicechat.llm.prompts import llama_sales

if __name__ == "__main__":
    device = 'cuda'

    print('loading models... ', device)

    ear = Ear(silence_seconds=2, device=device)
    john = Chatbot(sys_prompt=llama_sales)
    mouth = Mouth(device=device)
    mouth.say_text('Good morning!')
    run_chat(mouth, ear, john, verbose=True)
