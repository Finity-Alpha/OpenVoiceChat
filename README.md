# Voice Chat

Trying to create a pipeline where I can talk to an LLM.

STT + LLM + TTS

## What models should be used?

| STT | TTS | LLM |
| --- | --- | --- |
| [VITS](https://jaywalnut310.github.io/vits-demo/index.html) | [Whisper](https://github.com/openai/whisper) | [gpt-neo](https://huggingface.co/EleutherAI/gpt-neo-2.7B) atm |



## TODO:
- [x] ~~Fix LLM log (or atleast test it to make sure it works)~~ seems to work
- [ ] Handle interruptions
- [ ] Better LLM prompt


## Notes
How to handle interruptions? We constantly listen and transcribe and then stop tts. TTS has to stop on a word to make it natural. 
Also do we even stop. Sometimes the other person just says "yes" or "yeah".