#!/usr/bin/env python3.7
import hashlib
import os
import sys
import tempfile

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

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


def build_sentences(results):
    sentences = []
    for result in results:
        alt = result.alternatives[0]
        start_time = alt.words[0].start_time
        cur_start = start_time.seconds + start_time.nanos / 1e9
        cur_sentence = ""

        # we will keep consuming transcript as we go through words
        transcript = alt.transcript
        for word in alt.words:
            # add spaces to sentence, but don't treat them as end of sentence
            if transcript[0] in " ":
                transcript = transcript[1:]
                cur_sentence += " "
            # punctuation means end of sentence
            elif transcript[0] in "。，":
                # trim punctuation
                transcript = transcript[1:]
                word_end = word.end_time.seconds + word.end_time.nanos / 1e9
                # save current sentence and reset
                sentences.append((cur_sentence, cur_start, word_end))
                cur_sentence = ""
                cur_start = word_end

            assert transcript[0] == word.word[0], (transcript[0], word.word[0])
            cur_sentence += word.word
            transcript = transcript[len(word.word) :]
        if cur_sentence:
            word_end = word.end_time.seconds + word.end_time.nanos / 1e9
            sentences.append((cur_sentence, cur_start, word_end))
    return sentences


def print_res(response):
    print("Transcript: ")
    for result in response.results:
        alt = result.alternatives[0]
        print(alt.transcript)
    print()
    sentences = build_sentences(response.results)
    for sentence, start_time, end_time in sentences:
        print(f"{start_time} - {end_time}: {sentence}")
    print()


def get_response(uri):
    # look for cached response
    hash_ = hashlib.md5(uri.encode("utf-8")).hexdigest()
    try:
        tmp_dir = os.path.join(tempfile.gettempdir(), "cae")
        os.makedirs(tmp_dir, exist_ok=True)
        filename = os.path.join(tmp_dir, f"{hash_}.buf")
        with open(filename, "rb") as f:
            buf = types.LongRunningRecognizeResponse()
            buf.ParseFromString(f.read())
            return buf
    except:
        pass

    # no luck, do the conversion
    response = do_convert(uri)
    try:
        assert response.results[0].alternatives[0].words[0]
    except IndexError:
        print(f"No output: {uri}", file=sys.stderr)
        raise
    with open(filename, "wb") as f:
        f.write(response.SerializeToString())
    return response


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(sys.argv)
        print(f'usage: {sys.argv[0]} URI')
        sys.exit(1)
    uri = sys.argv[1]
    res = get_response(uri)
    print_res(res)
