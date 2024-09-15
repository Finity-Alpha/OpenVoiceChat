if __name__ == "__main__":
    from base import BaseChatbot
else:
    from .base import BaseChatbot


class Chatbot_llama(BaseChatbot):
    def __init__(
        self,
        model_path="models/llama-2-7b-chat.Q4_K_M.gguf",
        device="cuda",
        sys_prompt="",
        chat_format=None,
        temperature=0.7,
    ):

        from llama_cpp import Llama

        self.model = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_gpu_layers=-1 if device == "cuda" else 0,
            verbose=False,
            chat_format=chat_format,
        )
        self.messages = [{"role": "system", "content": sys_prompt}]
        self.temperature = temperature

    def run(self, input_text):
        self.messages.append({"role": "user", "content": input_text})
        out = self.model.create_chat_completion(
            self.messages, stream=True, temperature=self.temperature
        )
        response_text = ""
        for o in out:
            if "content" in o["choices"][0]["delta"].keys():
                text = o["choices"][0]["delta"]["content"]
                response_text += text
                yield text
            if o["choices"][0]["finish_reason"] is not None:
                break

    def post_process(self, response):
        self.messages.append({"role": "assistant", "content": response})
        return response


if __name__ == "__main__":
    from prompts import llama_sales as preprompt

    john = Chatbot_llama(
        model_path="../../models/llama-2-7b-chat.Q4_K_M.gguf",
        sys_prompt=preprompt,
        chat_format="llama-2",
    )
    print("type: exit, quit or stop to end the chat")
    print("Chat started:")
    while True:
        user_input = input(" ")
        if user_input.lower() in ["exit", "quit", "stop"]:
            break

        response = john.generate_response(user_input)

        print(response)
