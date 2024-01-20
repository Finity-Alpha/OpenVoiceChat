# Some Ideas


## Speculative decoding of whisper output

We can stream the output of whisper and have an LLM predict what the person will say next (also predicting what 
the bot will say). Do beam search and keep the beams that were correct according to the whisper output.
This is like "thinking while listening". 


## Interuptions

We constantly listen and transcribe and then stop tts. 
TTS has to stop on a word to make it natural. 
Also do we even stop. Sometimes the other person just says "yes" or "yeah". 
The stop recording policy is bad, it just stops recording after x number of silent seconds. 
There should be an EOS predictor for whisper, and we should stop using it, 
this will allow having pauses in the middle.
Use the whisper no speech tag as well.
Some good ideas [here](https://alphacephei.com/nsh/2023/09/22/time-brain-ctc-blank.html).