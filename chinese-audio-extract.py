#!/usr/bin/env python3.7
import io
import wave

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

import audioread

# Instantiates a client
client = speech.SpeechClient()

# The name of the audio file to transcribe
file_name = '/Users/ngarvey/Dropbox/Chinese/HSK Books/Book 2/15-2.mp3'

# Loads the audio into memory

with audioread.audio_open(file_name) as f:
    if file_name.endswith('.mp3'):
        with io.BytesIO() as buf, wave.open(buf, 'w') as wav:
            wav.setnchannels(f.channels)
            wav.setframerate(f.samplerate)
            wav.setsampwidth(2)
            for audio_buf in f:
                wav.writeframes(audio_buf)
            content = buf.getvalue()
    else:
        content = audio_file.read()
    audio = types.RecognitionAudio(content=content)

print(dir(enums.RecognitionConfig.AudioEncoding))

config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    language_code='zh')

# Detects speech in the audio file
response = client.recognize(config, audio)
print(type(response))

for result in response.results:
    print('Transcript: {}'.format(result.alternatives[0].transcript))
