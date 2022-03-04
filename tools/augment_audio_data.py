import librosa
import soundfile as sf
import random
import numpy as np
import os

# On getting "OSError: sndfile library not found" error like this - https://stackoverflow.com/questions/62337445/i-am-getting-oserror-sndfile-library-not-found-unable-to-locate-package-li
# Fix:
# 1. brew install libsndfile
# 2. The working dir might still not see the library, make a symbolic link of `libsndfile.dylib` within the dir.

def change_pitch(path):
    filename = path.removesuffix(".wav")
    audio, sampling_rate = librosa.load(path)

    converted_audio = librosa.effects.pitch_shift(audio, sr=sampling_rate, n_steps=random.choice([1, -1]))
    sf.write("augmented_files/" + filename + '_pitch_changed.wav', converted_audio, sampling_rate, 'PCM_16')

def change_speed(path):
    filename = path.removesuffix(".wav")
    audio, sampling_rate = librosa.load(path)
    original_audio_length = audio.size

    stretched_audio = librosa.effects.time_stretch(audio, rate=random.choice([0.8, 1.2]))
    converted_audio = librosa.util.fix_length(stretched_audio, size=original_audio_length)
    sf.write("augmented_files/" + filename + '_speed_changed.wav', converted_audio, sampling_rate, 'PCM_16')

def inject_noise(path):
    filename = path.removesuffix(".wav")
    audio, sampling_rate = librosa.load(path)

    noise = np.random.randn(len(audio))
    noise_factor = 0.01
    augmented_audio = audio + noise_factor * noise
    sf.write("augmented_files/" + filename + '_noise_injected.wav', augmented_audio, sampling_rate, 'PCM_16')

def shift_time(path):
    filename = path.removesuffix(".wav")
    audio, sampling_rate = librosa.load(path)
    # Maximum seconds to shift
    shift_max = 0.2

    shift = np.random.randint(sampling_rate * shift_max)
    # 0 is back forward and 1 is fast forward
    direction = np.random.randint(0, 2)
    if direction == 1:
        shift = -shift
    augmented_audio = np.roll(audio, shift)
    if shift > 0:
        augmented_audio[:shift] = 0
    else:
        augmented_audio[shift:] = 0
    sf.write("augmented_files/" + filename + '_time_shifted.wav', augmented_audio, sampling_rate, 'PCM_16')

def perform_data_augmentation(path):
    # Choose one of the data augmentation techniques and apply it.

    # Switch statement
    options = {0 : change_pitch,
               1 : change_speed,
               2 : inject_noise,
               3 : shift_time
              }
    choice = random.choice([0, 1, 2, 3])
    options[choice](path)

def augment_audio_data():
    for file in os.listdir("./"):
        if file.endswith(".wav"):
            perform_data_augmentation(file)

augment_audio_data()
