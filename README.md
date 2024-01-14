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
- [x] ~~Fix LLM log (or atleast test it to make sure it works)~~ seems to work
- [ ] Handle interruptions (doing in the "interruptions" branch)


## Notes
How to handle interruptions? We constantly listen and transcribe and then stop tts. TTS has to stop on a word to make it natural. 
Also do we even stop. Sometimes the other person just says "yes" or "yeah". The stop recording policy is bad, it just stops recording after x
number of silent seconds. There should be an EOS predictor for whisper and we should stop using it, this will allow having pauses in the middle.
Done some work on the [interruptions branch](https://github.com/fakhirali/VoiceChat/tree/interuptions). Just flags 
interrupt on some sound. Don't know how to handle 'yes' or 'yeah' yet. Will try to run the stt in another thread next.
Some ideas at [Ideas.md](Ideas.md)


