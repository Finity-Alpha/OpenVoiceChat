# Other Voice Chat solutions on the market

## Commercial

### [Retell AI](https://www.retellai.com/)

Same thing. Everyone is doing it. They give some info about 
what they are doing [here](https://docs.retellai.com/blog/build-voice-agent)
They have a turn taking model.

### [Sindrin tech](https://smarterchild.chat/)

This it the best one so far. Very very fast.
But interruptions are not great. It speaks over me a lot.

### [Vapi AI](https://vapi.ai/)

Similar to Retell AI, they also have an endpointing model.

### [Play AI](https://play.ai/)

Allows voice cloning.


## Open Source

### [Bud-e](https://github.com/LAION-AI/natural_voice_assistant)

A project by LAION AI. The code base is not very clean.
Seems like a standalone project. Very talented people working.
Good discussion and research on their discord.
Interruptions aren't really robust to umms and ahs.
Signal strength based VAD. They calc attention kvs while 
stt is running which is good. They say the biggest bottleneck 
is waiting for a sentence to TTS.
Their [roadmap](https://laion.ai/blog/bud-e/#a-roadmap-towards-empathic--natural-ai-voice-assistants) is very cool. 
They aim for a speech to speech model for chat.

### [Vocode](https://github.com/vocodedev/vocode-python)

Also have a hosted version [company](https://www.vocode.dev/).
Codebase is bad again. Not clear if they support interruptions.

### [Bolna AI](https://github.com/bolna-ai/bolna)

Very very similar to ovc. Codebase a little complicated. 
Business model is good. Good features, has twillo support,
uses tts, stt, llm services. Also supports local models.
Also very fast. 


### [Tincans](https://tincans.ai/)

Making Speech language models. Very impressive.
We should also train adapters for stt -> llm and llm -> tts models.
