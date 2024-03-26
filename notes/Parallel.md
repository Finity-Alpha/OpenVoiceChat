# Very Parallel Design

Two threads. One plays audio, the other one listens to it. 
These threads run in parallel continuously.

There are two queues. One for audio to be played, the other for audio to be listened to.

LLM, STT and TTS threads process the data in the queues.


