from llm_llama import Chatbot
from tts import Mouth
from stt import Ear
import torch
from preprompts import llama_sales
import torchaudio
import torchaudio.functional as F

if __name__ == "__main__":
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print('loading models...')

    ear = Ear(device=device, silence_seconds=4)
    audio, sr = torchaudio.load('media/test.wav')
    audio = F.resample(audio, sr, 16_000)[0]
    ear.transcribe(audio)

    john = Chatbot(device=device, sys_prompt=llama_sales)
    # john.generate_response('hello', c)

    mouth = Mouth(speaker_id=5, device=device, visualize=False)
    # mouth.say('Good morning! Thank you for calling Apple. My name is John, how can I assist you today?')
    mouth.say('Good morning!')

    # preprompt = sales_pre_prompt
    # preprompt = advisor_pre_prompt
    print("type: exit, quit or stop to end the chat")
    print("Chat started:")
    while True:
        # user_input = input(" ")
        user_input = ear.listen()
        if user_input.lower() in ["exit", "quit", "stop"]:
            break
        print(user_input)
        response = john.generate_response(user_input)
        print(response)

        mouth.say(response)
        if response.find('[END]') != -1:
            break
