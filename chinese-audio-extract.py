#!/usr/bin/env python3.7
import hashlib

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# URI of the file to transcript
URI = "gs://textbook-audio/textbook2_flac/02 第15课 课文二.flac"


def do_convert(uri):
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
        enable_automatic_punctuation=True,
        enable_word_time_offsets=True,
        language_code="zh",
    )

    audio = types.RecognitionAudio(uri=uri)

    client = speech.SpeechClient()
    # long_running_recognize because the files are larger than 1 minute
    response = client.long_running_recognize(config, audio)
    return response.result()


def print_res(response):
    for result in response.results:
        for alt in result.alternatives:
            print("Transcript: {}".format(alt.transcript))


def get_response(uri):
    # look for cached response
    hash = hashlib.md5(uri.encode("utf-8")).hexdigest()
    filename = f"/tmp/{hash}.buf"
    try:
        with open(filename, "rb") as f:
            buf = types.LongRunningRecognizeResponse()
            buf.ParseFromString(f.read())
            return buf
    except:
        pass

    # no luck, do the conversion
    response = do_convert(uri)
    with open(filename, "wb") as f:
        f.write(response.SerializeToString())
    return response


if __name__ == "__main__":
    res = get_response(URI)
    print_res(res)
