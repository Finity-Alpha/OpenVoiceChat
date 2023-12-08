from preprompts import llama_sales
from llama_cpp import Llama



class Chatbot:
    def __init__(self, model_path='models/llama-2-7b-chat.Q4_K_M.gguf', device='cuda', sys_prompt=''):
        if device == 'cuda':
            self.model = Llama(model_path=model_path, n_ctx=4096, n_gpu_layers=300, chat_format='llama-2',
                               stop=['[/INST]'], verbose=False)
        else:
            self.model = Llama(model_path=model_path, n_ctx=4096, chat_format='llama-2', stop=['[/INST]'],
                               verbose=False)
        self.messages = [{'role': 'system', 'content': sys_prompt}]
        self.model.create_chat_completion(messages=self.messages)




    def generate_response(self, input_text):
        self.messages.append({'role': 'user', 'content': input_text})
        out = self.model.create_chat_completion(messages=self.messages)
        response_text = out['choices'][0]['message']['content']
        self.messages.append({'role': 'assistant', 'content': response_text})
        return response_text


if __name__ == "__main__":
    preprompt = llama_sales
    john = Chatbot(sys_prompt=llama_sales)
    print("type: exit, quit or stop to end the chat")
    print("Chat started:")
    while True:
        user_input = input(" ")
        if user_input.lower() in ["exit", "quit", "stop"]:
            break

        response = john.generate_response(user_input)
        print(response)
