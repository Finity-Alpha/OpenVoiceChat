
<div align="center">

![logo](docs/main_logo.png)


<h3>
Have a natural voice conversation with an LLM

[Homepage](https://www.finityalpha.com/OpenVoiceChat/) | [Documentation](https://www.finityalpha.com/OpenVoiceChat/docs/) | [Discord](https://discord.gg/M5S2JksapH)

</h3>

</div>

---

https://github.com/fakhirali/OpenVoiceChat/assets/32309516/88b7973d-a362-46f3-ab18-232bb59a188e

### pip installation
```shell
pip install openvoicechat
```

### To install base and functionality specific packages
```shell
pip install openvoicechat[piper,openai,transformers]
```

similarly "piper" and "openai" can be replaced by any of the following
- piper (does not work on windows)
- vosk
- openai
- tortoise
- xtts
- transformers

```shell 
python main.py
```

[local Installation](INSTALL.md).

### Features

Supports practically any stt, tts and llm [model](notes/Models.md).

Supports interruptions.

Well [abstracted](/openvoicechat/tts) apis, easy to use and [extend](docs/Adding_models.md).

The goal is to be the open source alternative to [closed commercial implementations](notes/Competition.md)

Some ideas are [here](notes/Ideas.md). 

### Contributing
Start with the [bounties](https://docs.google.com/spreadsheets/d/1d2MZTa9FKM4IHLrBs_nMuA2yuLaSY4USzdGH6vRdPbU/edit?usp=sharing) 
if you want to contribute.

Roadmap [here](notes/Roadmap.md)

[Discord](https://discord.gg/M5S2JksapH)
