# TODO


Documentation and Doc string for functions

Send llama model to llm instead of instantiating it in the class.
Gives more control over the model.

Make it a pip package

Ollama support

Timing code is bad. Should be able to time better. 
Some inspiration is [here](https://github.com/LAION-AI/natural_voice_assistant).

No interruption info to the LLM. The interruption stt is also not sent anywhere.

Solve underruns by filling in [silence](https://stackoverflow.com/questions/19230983/prevent-alsa-underruns-with-pyaudio)

Web interface/API. Two websockets, audio in and audio out.

Turn Taking model? Retell seems to be doing it. And Vapi ai.

We don't have a good visualizer. And other UI is good.

Tortoise needs to be implemented properly.

Good demo videos showing interruptions and response time etc.

~~Elevenlabs is a bit slow when pauses. Make it so we don't wait
for the tts to finish before starting the next one.~~

~~There should be a better way to import different things from stt and tts etc.~~

~~OpenAI GPT API support~~

~~Write Docs to add any custom model~~
