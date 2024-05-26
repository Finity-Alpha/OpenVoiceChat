from setuptools import setup, find_packages

setup(
    author='Fakhir Ali',
    author_email='ali.fakhir33@gmail.com',
    description='OpenVoiceChat is an opensource library that allows you to have a natural voice conversation with '
                'your LLM agent.',
    long_description='If you plan on making an LLM agent and want to have your users be able to talk to it like a '
                     'person (low latency, handles interruptions), this library is for you. It aims to be the '
                     'opensource, highly extensible and easy to use alternative to the proprietary solutions.',
    url='http://www.fakhirali.pk/OpenVoiceChat/',
    name='openvoicechat',
    version='0.1.5',
    packages=find_packages(),
    install_requires=[
        'sounddevice',
        'pygame',
        'pyaudio',
        'librosa',
        'pydub',
        'python-dotenv',
        'websockets',
        'fastapi'
    ],
    extras_require={
        'transformers': ['transformers'],
        'piper': ['piper-tts', 'piper-phonemize'],
        'vosk': ['vosk'],
        'openai': ['openai'],
        'tortoise': ['tortoise-tts'],
        'xtts': ['TTS'],
    },
    dependency_links=[],
)
