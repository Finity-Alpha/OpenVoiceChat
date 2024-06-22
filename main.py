import os
from openvoicechat.tts.tts_hf import Mouth_hf as Mouth
from openvoicechat.llm.llm_gpt import Chatbot_gpt as Chatbot
from openvoicechat.llm.base import BaseChatbot
from openvoicechat.stt.stt_hf import Ear_hf as Ear
from openvoicechat.utils import run_chat
from openvoicechat.llm.prompts import llama_sales
from together import Together
from dotenv import load_dotenv
load_dotenv()

class Chatbot_together(BaseChatbot):
    def __init__(self, sys_prompt='', Model='mistralai/Mixtral-8x7B-Instruct-v0.1'):
        api_key = os.getenv("TOGETHER_API_KEY")
        print(api_key)
        self.MODEL = Model
        self.client = Together(api_key=api_key)
        self.messages = []
        self.messages.append({"role": "system", "content": sys_prompt})

    def run(self, input_text):
        self.messages.append({"role": "user", "content": input_text})

        stream = self.client.chat.completions.create(
            model=self.MODEL,
            messages=self.messages,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def post_process(self, response):
        self.messages.append({"role": "assistant", "content": response})
        return response
    
if __name__ == "__main__":
    device = 'cpu'

    print('loading models... ', device)

    ear = Ear(silence_seconds=2)

    load_dotenv()

    chatbot = Chatbot_together(sys_prompt=llama_sales)

    mouth = Mouth()

    run_chat(mouth, ear, chatbot, verbose=True, stopping_criteria=lambda x: '[END]' in x)
