# Voice Chat

Trying to create a pipeline where I can talk to an LLM.

STT + LLM + TTS

## What models should be used?

| STT | TTS | LLM |
| --- | --- | --- |
| [VITS](https://jaywalnut310.github.io/vits-demo/index.html) | [Whisper](https://github.com/openai/whisper) | [gpt-neo](https://huggingface.co/EleutherAI/gpt-neo-2.7B) atm |



## TODO:
- [ ] Fix LLM log (or atleast test it to make sure it works)
- [ ] Handle interruptions
- [ ] Better LLM prompt


## Notes:
Takes around 4GB GPU VRAM. Vits sounds very good and is fast. 