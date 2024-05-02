# Working

### How are interruptions handled?

The [base ear class](../stt/base.py) has a interrupt_listen function.
The function calls the record_interruption function from [utils.py](../utils.py).
The record_interruption function records audio and runs [silero-vad](../vad.py) on the last 2 seconds
if speech is detected then the audio is returned to the interrupt_listen function.
Inside the interrupt_listen function the audio is transcribed and if the transcription 
contains anything other than the ignored words (hmm, yeah etc.) the function returns True.
The interrupt_listen function is called in the say function of [base mouth class](../tts/base.py).
If the interrupt_listen function returns True then the say function stops playing the audio and sets 
the interruption flag to True.

### Low Latency stuff

The record_user function in [utils.py](../utils.py) records until 2 seconds of non VAD audio is detected.
Then the audio is transcribed and sent to the llm. The llm streams the response token by token. 
Once a sentence is completed the llm sends it to the [mouth class](../tts/base.py) for tts. The tts gets played and 
each successive sentence's tts output is queued up.


