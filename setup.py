from setuptools import setup, find_packages

setup(
    name='openvoicechat',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'sounddevice',
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
        'transformers' : ['transformers'],
        'piper': ['piper-tts','piper-phonemize'],
        'vosk': ['vosk'],
        'llama': ['llama-cpp-python'],
        'open_ai': ['openai'],
        'tortoise': ['tortoise-tts'],
        'xtts': ['TTS'],
    },
    dependency_links=[],
)