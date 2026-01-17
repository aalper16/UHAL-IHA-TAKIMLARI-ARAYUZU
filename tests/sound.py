import numpy as np
import pygame

pygame.mixer.init(frequency=44100, size=-16, channels=1)

def play_tone(frequency=440, duration=0.2, volume=0.5):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    
    # Sinüs dalgası üretimi
    waveform = np.sin(2 * np.pi * frequency * t)
    
    # 16-bit PCM’e dönüştür
    waveform = (waveform * 32767).astype(np.int16)
    
    # pygame ses nesnesi oluştur
    sound = pygame.sndarray.make_sound(waveform)
    sound.set_volume(volume)
    sound.play()
    
    # Sesin bitmesini bekle
    pygame.time.wait(int(duration * 1000))

# Örnek: 3 farklı frekansta ton
play_tone(400, 0.2)
play_tone(800, 0.2)
play_tone(1200, 0.2)