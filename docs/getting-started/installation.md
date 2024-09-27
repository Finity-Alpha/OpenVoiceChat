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
| TTS      | [Piper](https://github.com/rhasspy/piper.git)                | ```pip install piper-tts piper-phonemize```                 |
| TTS      | [xtts - Coqui](https://github.com/coqui-ai/TTS)                 | `pip install TTS phonemizer`                  |
| ALL      | [transformers - HuggingFace](https://huggingface.co/docs/transformers/index)     | `pip install transformers`          |
| LLM      | [Ollama](https://ollama.com/)               | `pip install ollama`                |
| LLM      | [OpenAI](https://github.com/openai/openai-python)               | `pip install openai`                |


Below you can select the required packages, and the `pip install` command will be generated automatically:

<div id="pip-install-generator">
    <h2>Select Required Packages</h2>
    <div class="package-selection">
        <input type="checkbox" id="transformers" value="transformers" onchange="generateCommand()">
        <label for="transformers">HuggingFace - transformers</label><br>
        <input type="checkbox" id="ollama" value="ollama" onchange="generateCommand()">
        <label for="ollama">Ollama</label><br>
        <input type="checkbox" id="openai" value="openai" onchange="generateCommand()">
        <label for="openai">OpenAI</label><br>
        <input type="checkbox" id="piper" value="piper-tts piper-phonemize" onchange="generateCommand()">
        <label for="piper">Piper-tts</label><br>
        <input type="checkbox" id="xtts" value="TTS phonemizer" onchange="generateCommand()">
        <label for="xtts">xtts</label><br>
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
        selectedPackages.shift();
        console.log(selectedPackages);
        let command = "pip install " + (selectedPackages.length > 0 ? selectedPackages.join(" ") : "<package_name>");
        document.getElementById("result").innerText = command;
    }
</script>
