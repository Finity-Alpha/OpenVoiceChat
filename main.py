from openvoicechat.tts.tts_elevenlabs import Mouth_elevenlabs as Mouth
from openvoicechat.llm.base import BaseChatbot
from openvoicechat.stt.stt_hf import Ear_hf as Ear
from openvoicechat.utils import run_chat
from openvoicechat.llm.prompts import llama_sales
from dotenv import load_dotenv
import os
from together import Together
import pandas as pd

class Chatbot_together(BaseChatbot):
    def __init__(self, api_key=None, sys_prompt=None, Model=None):
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("TOGETHER_API_KEY")
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

    columns = ['Model','Time Taken']
    df = pd.DataFrame(columns=columns)
    file_path = 'timing.csv'
    df.to_csv(file_path, index=False)

    ear = Ear(silence_seconds=2)

    load_dotenv()
    api_key = os.getenv("TOGETHER_API_KEY")

    chatbot = Chatbot_together(sys_prompt=llama_sales,
                      api_key=api_key, Model="mistralai/Mistral-7B-Instruct-v0.3")

    mouth = Mouth()
    # mouth = Mouth(device=device,
    #               forward_params={"speaker_id": 10})
    # mouth.say_text('Good morning!')
    run_chat(mouth, ear, chatbot, verbose=True,stopping_criteria=lambda x: '[END]' in x)
