if __name__ == "__main__":
    from base import BaseChatbot
else:
    from .base import BaseChatbot
import os
import json
import random
from openai._types import NOT_GIVEN


class Chatbot_gpt(BaseChatbot):
    def __init__(
        self,
        sys_prompt="",
        Model="gpt-4o-mini",
        api_key="",
        tools=None,
        tool_choice=NOT_GIVEN,
        tool_utterances=None,
        functions=None,
    ):

        if tools is None:
            tools = NOT_GIVEN
        if tool_utterances is None:
            tool_utterances = {}
        if functions is None:
            self.functions = {}

        from openai import OpenAI
        from dotenv import load_dotenv

        if api_key == "":
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")

        self.MODEL = Model
        self.client = OpenAI(api_key=api_key)
        self.messages = []
        self.messages.append({"role": "system", "content": sys_prompt})
        self.tools = tools
        self.tool_choice = tool_choice
        self.tool_utterances = tool_utterances
        self.functions = functions

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
                tool_choice=self.tool_choice,
            )

            for chunk in stream:
                finish_reason = chunk.choices[0].finish_reason
                if chunk.choices[0].delta.tool_calls is not None:
                    function_call_detected = True
                    tool_call = chunk.choices[0].delta.tool_calls[0]
                    if tool_call.function.name:
                        func_call["name"] = tool_call.function.name
                        func_call["id"] = tool_call.id
                        func_call["arguments"] = ""
                        # Choose a utterance for the tool at random and output it for the tts
                        yield random.choice(
                            self.tool_utterances[func_call["name"]]
                        ) + " . "  # the period is to make
                        # it say immediately
                    if tool_call.function.arguments:
                        func_call["arguments"] += tool_call.function.arguments
                if function_call_detected and finish_reason == "tool_calls":
                    self.messages.append(
                        {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": func_call["id"],
                                    "type": "function",
                                    "function": {
                                        "name": func_call["name"],
                                        "arguments": func_call["arguments"],
                                    },
                                }
                            ],
                        }
                    )
                    # run the function
                    function_response = self.functions[func_call["name"]](
                        **json.loads(func_call["arguments"])
                    )
                    self.messages.append(
                        {
                            "tool_call_id": func_call["id"],
                            "role": "tool",
                            "name": func_call["name"],
                            "content": function_response,
                        }
                    )
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                if finish_reason == "stop":
                    finished = True

    def post_process(self, response):
        # remove the tool utterances from the response
        # for tool in self.tool_utterances:
        #     response = response.replace(self.tool_utterances[tool], '')
        self.messages.append({"role": "assistant", "content": response})
        return response


if __name__ == "__main__":
    preprompt = "You are a helpful assistant."
    john = Chatbot_gpt(sys_prompt=preprompt)
    print("type: exit, quit or stop to end the chat")
    print("Chat started:")
    while True:
        user_input = input(" ")
        if user_input.lower() in ["exit", "quit", "stop"]:
            break

        response = john.generate_response(user_input)

        print(response)
