from openvoicechat.tts.tts_elevenlabs import Mouth_elevenlabs as Mouth
from openvoicechat.llm.llm_gpt import Chatbot_gpt as Chatbot
from openvoicechat.stt.stt_hf import Ear_hf as Ear
from openvoicechat.utils import run_chat
from openvoicechat.llm.prompts import llama_sales
from dotenv import load_dotenv
import os
import pandas as pd

if __name__ == "__main__":
    device = 'cpu'

    print('loading models... ', device)



    columns = ['Response','stt', 'tts', 'llm']
    df = pd.DataFrame(columns=columns)
    file_path = 'timing.csv'
    df.to_csv(file_path, index=False)

    ear = Ear(silence_seconds=2)

    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    chatbot = Chatbot(sys_prompt=llama_sales,
                      api_key=api_key)


    g_api_key = os.getenv('ELEVENLABS_API_KEY')
    mouth = Mouth()
    run_chat(mouth, ear, chatbot, verbose=True, stopping_criteria=lambda x: '[END]' in x)
