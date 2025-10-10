import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import queue
import requests
import sys
import threading
import wave
from openvoicechat.listener import BaseListener
from openvoicechat.player import BasePlayer
from daily import *
from openvoicechat.tts.base import BaseMouth
from openvoicechat.stt.base import BaseEar

from openvoicechat.llm.llm_ollama import Chatbot_ollama
from openvoicechat.llm.llm_gpt import Chatbot_gpt_simple
from openvoicechat.utils import run_chat
from openvoicechat.llm.prompts import llama_sales
from openvoicechat.logging_utils import make_logger
import os
import torch
import numpy as np
import uuid

import torchaudio.functional as F

load_dotenv()

logger = make_logger(console_log=False)
# logger = None


class Mouth_service(BaseMouth):
    def __init__(self, player):
        super().__init__(sample_rate=24000, player=player, logger=logger)

    def run_tts(self, text):
        res = requests.post("http://localhost:8000/synthesize", data=text)

        return np.frombuffer(res.content, dtype=np.float32)


class Ear_service(BaseEar):
    def __init__(self, listener, silence_seconds=1.5):
        super().__init__(
            listener=listener,
            logger=logger,
            silence_seconds=silence_seconds,
            listen_interruptions=False,
        )

    def transcribe(self, audio: np.ndarray):
        res = requests.post("http://localhost:8000/transcribe", data=audio.tobytes())
        return res.json()["transcription"]


def create_daily_room(
    api_key, room_name=None, privacy="public", exp_hours=1, config=None
):
    """
    Create a Daily room using the REST API

    Args:
        api_key (str): Your Daily API key
        room_name (str, optional): Custom room name. If None, Daily will generate one
        privacy (str): Room privacy level ("public" or "private")
        exp_hours (int): Hours until room expires (default: 1 hour)
        config (dict, optional): Additional room configuration options

    Returns:
        dict: Room creation response or None if failed
    """
    url = "https://api.daily.co/v1/rooms"

    # Calculate expiration time (unix timestamp in seconds)
    exp_time = int((datetime.now() + timedelta(hours=exp_hours)).timestamp())

    # Build request payload
    payload = {"privacy": privacy, "properties": {"exp": exp_time}}

    # Add room name if provided
    if room_name:
        payload["name"] = room_name

    # Add additional config if provided
    if config:
        payload["properties"].update(config)

    # Set headers
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        room_data = response.json()
        print(f"✅ Room created successfully!")
        print(f"Room Name: {room_data['name']}")
        print(f"Room URL: {room_data['url']}")
        print(f"Privacy: {room_data['privacy']}")
        print(f"Expires: {datetime.fromtimestamp(room_data['config']['exp'])}")

        return room_data

    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating room: {e}")
        if hasattr(e.response, "text"):
            print(f"Response: {e.response.text}")
        return None


#
# This demo will join a Daily meeting and record the meeting audio into standard
# output. The recorded audio format has 16-bit per sample.
#
# Usage: python3 raw_audio_receive.py -m MEETING_URL > FILE.raw
#
# The following example shows how to send back the recorded audio using a
# GStreamer pipeline and raw_audio_send.py:
#
# gst-launch-1.0 -q filesrc location=FILE.raw ! \
#    rawaudioparse num-channels=1 pcm-format=s16le sample-rate=16000 ! \
#    fdsink fd=1 sync=true | python3 raw_audio_send.py -m MEETING_URL
#

import argparse
import sys
import threading
from openvoicechat.listener import BaseListener


from daily import *

SAMPLE_RATE = 16000
NUM_CHANNELS = 1
BYTES_PER_SAMPLE = 2


class Listener_daily(BaseListener):
    def __init__(self, samplerate, q):
        super().__init__(samplerate)
        self.input_queue = q
        self.listening = False
        self.CHUNK = int(samplerate * 1)
        self.RATE = samplerate

    def read(self, x):
        return self.input_queue.get()

    def close(self):
        self.listening = False
        self.input_queue.queue.clear()

    def make_stream(self):
        self.listening = True
        self.input_queue.queue.clear()
        return self


class Player_daily(BasePlayer):
    def __init__(self, q):
        super().__init__()
        self.output_queue = q
        self.playing = False
        self.sample_rate = SAMPLE_RATE
        self.num_channels = NUM_CHANNELS

    def play(self, audio_array, samplerate):
        self.playing = True
        if samplerate != self.sample_rate:
            audio_array = F.resample(
                torch.tensor(audio_array), samplerate, self.sample_rate
            )
            audio_array = audio_array.numpy()

        # Convert float32 audio to int16 properly before sending
        if audio_array.dtype != np.int16:
            audio_array = (audio_array * 32767).clip(-32768, 32767).astype(np.int16)
        audio_bytes = audio_array.tobytes()
        self.output_queue.put(audio_bytes)

    def wait(self):
        while not self.output_queue.empty():
            pass


class ReceiveAudioApp:
    def __init__(self, sample_rate, num_channels, listener, player):
        self.__sample_rate = sample_rate
        self.__num_channels = num_channels
        self.__listener = listener
        self.__player = player
        self.__speaker_device = Daily.create_speaker_device(
            "my-speaker",
            sample_rate=sample_rate,
            channels=num_channels,
            non_blocking=False,
        )

        self.__mic_device = Daily.create_microphone_device(
            "my-mic", sample_rate=sample_rate, channels=num_channels
        )
        Daily.select_speaker_device("my-speaker")

        self.__client = CallClient()
        self.__client.update_subscription_profiles(
            {"base": {"camera": "unsubscribed", "microphone": "subscribed"}}
        )
        self.__client.set_user_name("OpenVoiceChat")
        self.__client.update_inputs(
            {"microphone": {"isEnabled": True, "settings": {"deviceId": "my-mic"}}}
        )

        self.__app_quit = False
        self.__app_error = None

        self.__start_event = threading.Event()
        self.__thread_receive = threading.Thread(target=self.receive_audio)
        self.__thread_receive.start()
        self.__thread_send = threading.Thread(target=self.send_raw_audio)
        self.__thread_send.start()

    def on_joined(self, data, error):
        if error:
            print(f"Unable to join meeting: {error}")
            self.__app_error = error
        self.__start_event.set()

    def run(self, meeting_url):
        self.__client.join(
            meeting_url,
            client_settings={
                "inputs": {
                    "camera": False,
                    "microphone": {
                        "isEnabled": True,
                        "settings": {"deviceId": "my-mic"},
                    },
                }
            },
            completion=self.on_joined,
        )
        # self.__client.start_recording(
        #     layout={"preset": "audio-only"}, stream_id=str(uuid.uuid4())
        # )
        self.__thread_receive.join()
        self.__thread_send.join()

    def just_join(self, meeting_url):
        self.__client.join(
            meeting_url,
            client_settings={
                "inputs": {
                    "camera": False,
                    "microphone": {
                        "isEnabled": True,
                        "settings": {"deviceId": "my-mic"},
                    },
                }
            },
            completion=self.on_joined,
        )

    def leave(self):
        self.__app_quit = True
        self.__thread_receive.join()
        self.__thread_send.join()
        self.__client.leave()
        self.__client.release()

    def receive_audio(self):
        self.__start_event.wait()

        if self.__app_error:
            print(f"Unable to receive audio!")
            return

        while not self.__app_quit:
            buffer = self.__speaker_device.read_frames(int(self.__sample_rate * 1))
            if len(buffer) > 0:
                if self.__listener.listening:

                    self.__listener.input_queue.put(buffer)
                else:
                    pass
            else:
                pass

    def send_raw_audio(self):
        self.__start_event.wait()

        if self.__app_error:
            print(f"Unable to send audio!")
            return

        while not self.__app_quit:
            try:
                buffer = self.__player.output_queue.get_nowait()
                if buffer:
                    self.__mic_device.write_frames(buffer)
            except queue.Empty:
                continue


def read_audio(meeting_url):
    Daily.init()

    input_queue = queue.Queue()
    output_queue = queue.Queue()
    listener = Listener_daily(SAMPLE_RATE, input_queue)
    player = Player_daily(output_queue)
    app = ReceiveAudioApp(SAMPLE_RATE, NUM_CHANNELS, listener, player)
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    print("loading models... ", device)
    load_dotenv()
    ear = Ear_service(listener=listener, silence_seconds=1)

    chatbot = Chatbot_gpt_simple(
        sys_prompt=llama_sales, model="gpt-4.1-nano", logger=None
    )
    # chatbot = Chatbot_ollama(sys_prompt=llama_sales, model="qwen2:0.5b", logger=logger)

    mouth = Mouth_service(player=player)
    # run_chat_thread = threading.Thread(
    #     target=run_chat, args=(mouth, ear, chatbot, True)
    # )
    # run_chat_thread.start()

    try:
        app.just_join(meeting_url)
        run_chat(mouth, ear, chatbot, False, stopping_criteria=lambda x: "[END]" in x)
    except KeyboardInterrupt:
        print("Ctrl-C detected. Exiting!", file=sys.stderr)
    finally:
        # run_chat_thread.join()
        app.leave()


if __name__ == "__main__":
    # You need to set your Daily API key
    API_KEY = os.getenv("DAILY_API_KEY")  # Set this environment variable
    room = create_daily_room(API_KEY, privacy="public")
    print(room["url"])

    # Start recording service in background (non-blocking)
    import subprocess

    recording_cmd = [
        "python",
        "webrtc/recording_service.py",
        room["url"],
        "--output",
        "meeting_recording.wav",
    ]
    print(f"🎬 Starting recording service: {' '.join(recording_cmd)}")
    subprocess.Popen(recording_cmd)

    read_audio(room["url"])
