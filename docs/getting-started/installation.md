# Installation

### Requirements
- portaudio by running `sudo apt-get install portaudio19-dev `
- [torch](https://pytorch.org/get-started/locally/)
- [torchaudio](https://pytorch.org/get-started/locally/)
- 
### Model specific requirements
- [llama-cpp-python](https://llama-cpp-python.readthedocs.io/en/latest/)
Make sure to install it using the correct CMAKE flag(s).
- [onnxruntime-gpu](https://onnxruntime.ai/docs/install/)


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
- openai ([link](https://github.com/openai/openai-python))
- xtts ([link](https://github.com/coqui-ai/TTS))
- transformers ([link](https://github.com/huggingface/transformers))