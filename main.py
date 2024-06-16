import os

from openvoicechat.tts.tts_elevenlabs import Mouth_elevenlabs as Mouth
from openvoicechat.llm.llm_gpt import Chatbot_gpt as Chatbot
from openvoicechat.stt.stt_deepgram import Ear_deepgram as Ear
from openvoicechat.utils import run_chat
from openvoicechat.llm.prompts import llama_sales
from dotenv import load_dotenv
load_dotenv()


if __name__ == "__main__":
    device = 'cpu'

    print('loading models... ', device)
    api_key = os.getenv('DEEPGRAM_API_KEY')
    ear = Ear(silence_seconds=2, api_key=api_key)

    load_dotenv()

    chatbot = Chatbot(sys_prompt=llama_sales)

    mouth = Mouth()

    run_chat(mouth, ear, chatbot, verbose=True, stopping_criteria=lambda x: '[END]' in x)
