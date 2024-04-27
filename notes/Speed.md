# Speed

Notes on how to make ovc faster.

### With online services

We have no control over running the models.
We only have control over the input and output and how they are processed.
Umm and yeah maybe played after 0.5s or 1s of silence.
Speech endpointing is important. We need a classifier or smth that 
predicts if the user has stopped speaking or is taking a pause.
This will help in running the llm or tts or stt immediately.
Streaming transcription helps. Will cut down on the latency 
of sending the audio entirely and getting the text back.





