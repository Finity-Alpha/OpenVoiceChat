if __name__ == '__main__':
    from base import BaseChatbot
else:
    from .base import BaseChatbot
import os

class Chatbot_gpt(BaseChatbot):
    def __init__(self, sys_prompt='',
                 Model='gpt-3.5-turbo',
                 api_key='',
                 tools=None,
                 tool_choice="auto",
                 tool_utterances=None):
        if tools is None:
            tools = []
        if tool_utterances is None:
            tool_utterances = {}
        from openai import OpenAI
        from dotenv import load_dotenv
        if api_key == '':
            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')
        self.MODEL = Model
        self.client = OpenAI(api_key=api_key)
        self.messages = []
        self.messages.append({"role": "system", "content": sys_prompt})
        self.tools = tools
        self.tool_choice = tool_choice
        self.tool_utterances = tool_utterances

    def run(self, input_text):
        self.messages.append({"role": "user", "content": input_text})
        finished = False
        while not finished:

            func_call = dict()
            function_call_detected = False

            stream = self.client.chat.completions.create(
                model=self.MODEL,
                messages=self.messages,
                stream=True,
                tools=self.tools,
                tool_choice="auto",
            )
            for chunk in stream:
                finish_reason = chunk.choices[0].finish_reason
                if chunk.choices[0].delta.tool_calls is not None:
                    function_call_detected = True
                    tool_call = chunk.choices[0].delta.tool_calls[0]
                    if tool_call.function.name:
                        func_call["name"] = tool_call.function.name
                        func_call["id"] = tool_call.id
                        func_call['arguments'] = ''
                        yield func_utterance[func_call['name']]
                    if tool_call.function.arguments:
                        func_call["arguments"] += tool_call.function.arguments
                if function_call_detected and finish_reason == 'tool_calls':
                    self.messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": func_call['id'],
                                "type": "function",
                                "function": {
                                    "name": func_call['name'],
                                    "arguments": func_call['arguments']
                                }
                            }]
                    })
                    # run the function
                    function_response = eval(f"{func_call['name']}(**{func_call['arguments']})")
                    self.messages.append({
                        "tool_call_id": func_call['id'],
                        "role": "tool",
                        "name": func_call['name'],
                        "content": function_response,
                    })
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                if finish_reason == 'stop':
                    finished = True

    def post_process(self, response):
        self.messages.append({"role": "assistant", "content": response})
        return response


if __name__ == "__main__":
    preprompt = 'You are a helpful assistant.'
    john = Chatbot_gpt(sys_prompt=preprompt)
    print("type: exit, quit or stop to end the chat")
    print("Chat started:")
    while True:
        user_input = input(" ")
        if user_input.lower() in ["exit", "quit", "stop"]:
            break

        response = john.generate_response(user_input)

        print(response)
