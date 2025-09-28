import os
import sys
import argparse
import threading
import wave
from daily import *


SAMPLE_RATE = 16000
NUM_CHANNELS = 1
BYTES_PER_SAMPLE = 2


def open_wave_file(file_path, sample_rate=16000, channels=1, sample_width=2):
    """
    Always open a wave file for writing and configure its parameters.

    Args:
        file_path (str): Path to the wave file
        sample_rate (int): Sample rate in Hz (default: 16000)
        channels (int): Number of audio channels (default: 1 for mono)
        sample_width (int): Sample width in bytes (default: 2 for 16-bit)

    Returns:
        wave.Wave_write: Configured wave file object for writing
    """
    try:
        wf = wave.open(file_path, "wb")
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        return wf
    except Exception as e:
        print(f"Error opening wave file {file_path}: {e}")
        return None


class RecordAudioApp:
    def __init__(self, meeting_url, output_file="output.wav"):
        self.__speaker_device = Daily.create_speaker_device(
            "recording-speaker",
            sample_rate=SAMPLE_RATE,
            channels=NUM_CHANNELS,
            non_blocking=False,
        )
        Daily.select_speaker_device("recording-speaker")
        self.wf = open_wave_file(
            output_file,
            sample_rate=SAMPLE_RATE,
            channels=NUM_CHANNELS,
            sample_width=BYTES_PER_SAMPLE,
        )
        self.__client = CallClient()
        self.__client.set_user_name("OpenVoiceChat-Recorder")
        self.__client.update_subscription_profiles(
            {"base": {"camera": "unsubscribed", "microphone": "subscribed"}}
        )

        self.__app_quit = False
        self.__app_error = None
        self.__start_event = threading.Event()
        self.__thread_receive = threading.Thread(target=self.receive_audio)

    def on_joined(self, data, error):
        if error:
            print(f"Unable to join meeting: {error}")
            self.__app_error = error
        self.__start_event.set()

    def receive_audio(self):
        self.__start_event.wait()

        if self.__app_error:
            print(f"Unable to receive audio!")
            return

        while not self.__app_quit:
            buffer = self.__speaker_device.read_frames(int(SAMPLE_RATE / 10))
            if len(buffer) > 0:
                self.wf.writeframes(buffer)

    def leave(self):
        self.__app_quit = True
        self.__thread_receive.join()
        self.__client.leave()
        self.__client.release()
        self.wf.close()

    def run(self, meeting_url):
        self.__thread_receive.start()
        self.__client.join(meeting_url, completion=self.on_joined)
        self.__thread_receive.join()


def main():
    """
    Main function to run the recording service as a standalone script.

    Usage:
        python recording_service.py <meeting_url> [--output output.wav]
    """
    parser = argparse.ArgumentParser(
        description="Record audio from a Daily meeting to a WAV file"
    )
    parser.add_argument("meeting_url", help="Daily meeting URL to join and record")
    parser.add_argument(
        "--output",
        "-o",
        default="output.wav",
        help="Output WAV file path (default: output.wav)",
    )

    args = parser.parse_args()

    # Initialize Daily
    Daily.init()

    print(f"🎙️  Starting recording service...")
    print(f"📹 Meeting URL: {args.meeting_url}")
    print(f"💾 Output file: {args.output}")

    # Create and run recorder
    recorder = RecordAudioApp(args.meeting_url, args.output)

    try:
        recorder.run(args.meeting_url)
    except KeyboardInterrupt:
        print("\n⏹️  Ctrl-C detected. Stopping recording...")
    finally:
        recorder.leave()
        print("✅ Recording completed and saved!")


if __name__ == "__main__":
    main()
