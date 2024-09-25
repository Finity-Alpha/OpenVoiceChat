# Installation

### pip installation
```shell
pip install openvoicechat
```

### Other Requirements
- portaudio
- [torch](https://pytorch.org/get-started/locally/)
- [torchaudio](https://pytorch.org/get-started/locally/)

### Install model specific packages

| Category | Model Name           | Required Packages       |
|----------|----------------------|-------------------------|
| TTS      | Piper                | ```pip install piper-tts piper-phonemize```                 |
| TTS      | xtts                 | `pip install TTS phonemizer`                  |
| ALL      | HuggingFace     | `pip install transformers`          |
| LLM      | Ollama               | `pip install ollama`                |
| LLM      | OpenAI               | `pip install openai`                |


Below you can select the required packages, and the `pip install` command will be generated automatically:

<div id="pip-install-generator">
    <h2>Select Required Packages</h2>
    <div class="package-selection">
        <input type="checkbox" id="transformers" value="transformers" onchange="generateCommand()">
        <label for="transformers">HuggingFace (All) - transformers</label><br>
        <input type="checkbox" id="ollama" value="ollama" onchange="generateCommand()">
        <label for="ollama">Ollama - ollama</label><br>
        <input type="checkbox" id="openai" value="openai" onchange="generateCommand()">
        <label for="openai">OpenAI - openai</label><br>
        <input type="checkbox" id="deepgram-sdk" value="deepgram-sdk" onchange="generateCommand()">
        <label for="deepgram-sdk">Deepgram - deepgram-sdk</label><br>
        <input type="checkbox" id="elevenlabs" value="elevenlabs" onchange="generateCommand()">
        <label for="elevenlabs">ElevenLabs - elevenlabs</label><br>
        <input type="checkbox" id="pip3r" value="pip3r" onchange="generateCommand()">
        <label for="pip3r">Piper - pip3r</label><br>
        <input type="checkbox" id="xtts" value="xtts" onchange="generateCommand()">
        <label for="xtts">xtts - xtts</label><br>
    </div>
    <pre class="result"><code id="result">pip install <package_name></code></pre>
</div>

<script>
    function generateCommand() {
        let selectedPackages = [];
        const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
        checkboxes.forEach((checkbox) => {
            selectedPackages.push(checkbox.value);
        });

        let command = "pip install " + (selectedPackages.length > 0 ? selectedPackages.join(" ") : "<package_name>");
        document.getElementById("result").innerText = command;
    }
</script>
