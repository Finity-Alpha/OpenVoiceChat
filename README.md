
<div align="center">

![logo](media/logo.gif)

<h3>

Have a natural voice conversation with an LLM

</h3>

</div>

---

https://github.com/fakhirali/OpenVoiceChat/assets/32309516/88b7973d-a362-46f3-ab18-232bb59a188e


Supports all kinds of stt, tts and llm [models](notes/Models.md).

Supports interruptions.

Well [abstracted](/openvoicechat/tts) apis, easy to use and [extend](notes/Adding_models.md).

The goal is to be the open source alternative to [closed commercial implementations](notes/Competition.md)

Some ideas are [here](notes/Ideas.md). 

[TODO](notes/TODO.md).

Start with the [bounties](https://docs.google.com/spreadsheets/d/1d2MZTa9FKM4IHLrBs_nMuA2yuLaSY4USzdGH6vRdPbU/edit?usp=sharing) 
if you want to contribute.

[Installation](INSTALL.md).

```shell 
python main.py
```

[Discord](https://discord.gg/M5S2JksapH)

## Installing Required Packages
### To install only the base packages
```shell
pip install openvoicechat
```

### To install base and functionality specific packages
```shell
pip install openvoicechat[piper,openai,transformers]
```

similarly "piper" and "xtts" can be replaced by any of the following
- piper
- vosk
- openai
- tortoise
- xtts
- transformers