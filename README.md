# Voice Chat

Trying to create a pipeline where I can talk to an LLM.

STT + LLM + TTS

[some](./media/john_call_new.mp3) [examples](./media/john_call.mp3) (the examples shown are with gpt-neo, will update with llama soon)

### models used

| TTS                                                         | STT                                          | LLM                                                                    |
|-------------------------------------------------------------|----------------------------------------------|------------------------------------------------------------------------|
| [VITS](https://jaywalnut310.github.io/vits-demo/index.html) | [Whisper](https://github.com/openai/whisper) | [llama-7b-chat-q4](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF) |

Using [M4T](https://github.com/facebookresearch/seamless_communication) one model can do stt + tts + translation.
The translation [quality is almost](./media/translation_quality.png) there.

Now [uses](main_llama.py) llama 7B thanks to [llama cpp python](https://github.com/abetlen/llama-cpp-python)



## TODO:
- [ ] Fix streaming tortoise interruption
- [ ] Better tts abstractions with multiple and interruption

