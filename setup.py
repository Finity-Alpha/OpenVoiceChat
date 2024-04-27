from setuptools import setup, find_packages

setup(
    name='openvoicechat',
    version='2.0',
    packages=find_packages(),
    install_requires=[
        'sounddevice',
        'transformers',
        'torch',
        'torchaudio',
        'pygame',
        'pyaudio',
        'librosa',
        'pydub',
        'python-dotenv',
        'phonemizer',
        'websockets'
    ],
    extras_require={
        'piper': ['piper-tts','piper-phonemize'],
        'vosk': ['vosk'],
        'llama': ['llama-cpp-python'],
        'open_ai': ['openai'],
        'tortoise': ['tortoise-tts'],
        'xtts': ['TTS'],
        'parler_tts': ['parler-tts @ git+https://github.com/huggingface/parler-tts.git'],
    },
    dependency_links=['https://github.com/huggingface/parler-tts.git']
)