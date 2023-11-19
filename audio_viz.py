# music like audio visualization
# audio file is loaded and played
# and a pygame window shows the waveform as it is played


import numpy as np
import librosa
import pygame

# pygame setup
pygame.init()
pygame.mixer.init()
pygame.display.set_caption('audio visualization')
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# load audio file
audio_file = 'media/john_call.mp3'
y, sr = librosa.load(audio_file)
fft = librosa.stft(y)
frame_rate = sr / 512  # 512 is the window size
print(fft.shape)

# play audio
pygame.mixer.music.load(audio_file)
pygame.mixer.music.play()

# main loop
running = True
j = 0
total_frames = 0
while running:
    clock.tick(frame_rate)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # draw waveform
    screen.fill((0, 0, 0))
    freq_len = 100
    viz_width = 800 / freq_len
    for i in range(len(fft[:freq_len, j])):
        pygame.draw.line(screen, (255, 255, 255), ((i*viz_width), 300),
                         (i*viz_width, 300+float(fft[i][j])*5), 2)
    j += 1
    pygame.display.flip()
