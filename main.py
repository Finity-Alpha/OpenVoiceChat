from llm import Chatbot
from tts import Mouth
from stt import Ear
import torch
from preprompts import call_pre_prompt, sales_pre_prompt, advisor_pre_prompt
import torchaudio
import torchaudio.functional as F

if __name__ == "__main__":
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print('loading models...')

    ear = Ear(device=device, silence_seconds=2)
    audio, sr = torchaudio.load('media/test.wav')
    audio = F.resample(audio, sr, 16_000)[0]
    ear.transcribe(audio)

    john = Chatbot(device=device)
    john.generate_response_greedy('hello', call_pre_prompt, '[USER]')  # warmup

    mouth = Mouth(speaker_id=5, device=device, visualize=False)
    mouth.say('Good morning! Thank you for calling Apple. My name is John, how can I assist you today?')

    # preprompt = sales_pre_prompt
    # preprompt = advisor_pre_prompt
    preprompt = call_pre_prompt

    log = ''
    past_kv = None
    next_id = None
    print("type: exit, quit or stop to end the chat")
    print("Chat started:")
    while True:
        # user_input = input(" ")
        user_input = ear.listen()
        if user_input.lower() in ["exit", "quit", "stop"]:
            break
        break_word = '[USER]'
        name = '[JOHN]'
        print(user_input)
        response, past_kv, next_id = john.generate_response_greedy(user_input, preprompt + log,
                                                                   break_word, max_length=100000, name=name,
                                                                   past_key_vals=past_kv, next_id=next_id,
                                                                   verbose=True, temp=0.6)

        mouth.say(response.replace('[USER]', '').replace('[END]', '').replace('[START]', ''))

        log += ' ' + user_input + '\n' + name + response
        # print(' ' + user_input + '\n' + name + response)
        print(response)
        if response.find('[END]') != -1:
            break
