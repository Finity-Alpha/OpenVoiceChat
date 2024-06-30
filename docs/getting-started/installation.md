# Installation

### Requirements
- portaudio by running `sudo apt-get install portaudio19-dev `
- [onnxruntime-gpu](https://onnxruntime.ai/docs/install/)
### Model specific requirements
- [llama-cpp-python](https://llama-cpp-python.readthedocs.io/en/latest/)
Make sure to install it using the correct CMAKE flag(s).
- [torch](https://pytorch.org/get-started/locally/)
- [torchaudio](https://pytorch.org/get-started/locally/)


### pip installation
```shell
pip install openvoicechat
```

### To install base and functionality specific packages
```shell
pip install openvoicechat[piper,openai,transformers]
```

similarly "piper" and "openai" can be replaced by any of the following install options:

- piper ([link](https://github.com/rhasspy/piper)) (does not work on windows)
- vosk ([link](https://github.com/alphacep/vosk-api))
- openai ([link](https://github.com/openai/openai-python))
- tortoise ([link](https://github.com/neonbjb/tortoise-tts))
- xtts ([link](https://github.com/coqui-ai/TTS))
- transformers ([link](https://github.com/huggingface/transformers))