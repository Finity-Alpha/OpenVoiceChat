if __name__ == "__main__":
    from base import BaseChatbot
else:
    from .base import BaseChatbot


class Chatbot_ollama(BaseChatbot):
    def __init__(self, sys_prompt="", model="llama3"):
        import ollama

        ollama.pull(model)
        self.MODEL = model
        self.client = ollama
        self.messages = []
        self.messages.append({"role": "system", "content": sys_prompt})

    def run(self, input_text):
        self.messages.append({"role": "user", "content": input_text})
        stream = self.client.chat(
            model=self.MODEL,
            messages=self.messages,
            stream=True,
        )

        for chunk in stream:
            if chunk["message"]["content"] is not None:
                yield chunk["message"]["content"]

    def post_process(self, response):
        self.messages.append({"role": "assistant", "content": response})
        return response


if __name__ == "__main__":
    preprompt = "You are a helpful assistant."
    john = Chatbot_ollama(sys_prompt=preprompt)
    print("type: exit, quit or stop to end the chat")
    print("Chat started:")
    while True:
        user_input = input(" ")
        if user_input.lower() in ["exit", "quit", "stop"]:
            break

        response = john.generate_response(user_input)

        print(response)
