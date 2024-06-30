# Quickstart

Talk to a apple sales agent.

```py
import os
from openvoicechat.tts.tts_elevenlabs import Mouth_elevenlabs
from openvoicechat.llm.llm_gpt import Chatbot_gpt
from openvoicechat.stt.stt_hf import Ear_hf
from openvoicechat.utils import run_chat
from openvoicechat.llm.prompts import llama_sales
from dotenv import load_dotenv


if __name__ == "__main__":
    device = 'cuda'

    print('loading models... ', device)
    
    load_dotenv()
    elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
    gpt_api_key = os.getenv('OPENAI_API_KEY')
    
    ear = Ear_hf(silence_seconds=2, device=device)

    chatbot = Chatbot_gpt(sys_prompt=llama_sales, api_key=gpt_api_key)

    mouth = Mouth_elevenlabs(api_key=elevenlabs_api_key)

    run_chat(mouth, ear, chatbot, verbose=True,
             stopping_criteria=lambda x: '[END]' in x)
```





