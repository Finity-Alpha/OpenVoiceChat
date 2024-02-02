import numpy as np
import pyaudio
import audioop

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

def record_audio(record_seconds=100):
    # yield audio frames

    RECORD_SECONDS = record_seconds

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        yield data


def record_interruption(vad, recond_seconds=100):
    print("* recording for interruption")
    for data in record_audio(recond_seconds):
        contains_speech = vad.contains_speech([data])
        if contains_speech:
            return True
    return False



def record_user(silence_seconds, vad):
    print("* recording")
    frames = []

    started = False
    one_second_iters = int(RATE / CHUNK)
    for data in record_audio(100):
        frames.append(data)
        contains_speech = vad.contains_speech(frames[-one_second_iters*silence_seconds:])
        if not started and contains_speech:
            started = True
        if started and contains_speech is False:
            break

    print("* done recording")

    # creating a np array from buffer
    frames = np.frombuffer(b''.join(frames), dtype=np.int16)

    # normalization see https://discuss.pytorch.org/t/torchaudio-load-normalization-question/71470
    frames = frames / (1 << 15)

    return frames.astype(np.float32)
