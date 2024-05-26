from openvoicechat.tts.tts_piper import Mouth_piper as Mouth
from openvoicechat.llm.llm_gpt import Chatbot_gpt as Chatbot
from openvoicechat.stt.stt_hf import Ear_hf as Ear
from openvoicechat.utils import run_chat
from openvoicechat.llm.prompts import llama_sales
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    device = 'cuda'

    print('loading models... ', device)

    ear = Ear(silence_seconds=2, device=device)

    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    chatbot = Chatbot(sys_prompt=llama_sales,
                      api_key=api_key)
    mouth = Mouth(device=device)
    mouth.say_text('Good morning!')
    run_chat(mouth, ear, chatbot, verbose=True, stopping_criteria=lambda x: '[END]' in x)
