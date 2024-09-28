# Advanced Usage
Tips and tricks for getting the most out of OpenVoiceChat.

### [Key words]
Text surrounded in square brackets are not spoken by the tts model. This form of "tokens" can be used for stopping criteria, special commands, or other purposes.

### Stopping criteria

The `run_chat`(inside utils) function takes in a stopping criteria function that is called at the end of each turn. This function should return a boolean value indicating whether the chat should continue. By default, the stopping criteria function is `lambda x: False`, which does not stop the chat. You can pass in your own stopping criteria function to `run_chat` to customize when the chat should stop. For example `lambda x: "[END]" in x` will stop the chat when the model outputs the string "[END]".


### Integration with other audio streams

The `player` and `listener` classes are used to connect the audio pipeline with external audio streams. See the twilio or websocket player and listener for an example of how to integrate with external audio streams.



