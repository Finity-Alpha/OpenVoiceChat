import numpy as np
import pyaudio
import audioop
def record(silence_seconds):
    seconds_silence = silence_seconds  # changing this might make the convo more natural
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1  # make sure this is 1
    RATE = 16000
    RECORD_SECONDS = 100
    WAVE_OUTPUT_FILENAME = "user.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    started = False
    one_second_iters = int(RATE / CHUNK)
    silent_iters = 0

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        rms = audioop.rms(data, p.get_sample_size(FORMAT))
        decibel = 20 * np.log10(rms)
        if not started and decibel > 50:
            started = True

        if started and decibel < 50:
            silent_iters += 1

        if started and decibel > 50:
            silent_iters = 0

        if silent_iters >= one_second_iters * seconds_silence:
            break

    print("* done recording")

    # creating a np array from buffer
    frames = np.frombuffer(b''.join(frames), dtype=np.int16)

    # normalization see https://discuss.pytorch.org/t/torchaudio-load-normalization-question/71470
    frames = frames / (1 << 15)

    return frames.astype(np.float32)
