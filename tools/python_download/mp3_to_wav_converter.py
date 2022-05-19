# BEFORE:
# $ pip install pydub
# $ brew install ffmpeg

import os
from pydub import AudioSegment

# files
src = "./clips"
dst = "./clips/wav_converted"

for file in os.listdir(src):
    if file.endswith(".mp3"):
        sound = AudioSegment.from_mp3(os.path.join(src, file))
        filename = os.path.splitext(file)[0]
        sound.export("%s/%s.wav" %(dst, filename), format="wav")
