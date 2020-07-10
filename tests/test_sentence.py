import io
import os
import soundfile as sf

import __init__
from test_framework import test

# from src/
from sentence import Sentence, SynthesizedSentence
from constants.constants import TEST_DIR

cache = {}


def create_mock_translation(sentence, audio_file, lang):
    mock_translation = SynthesizedSentence("test", "test")
    # Length of this track ~ 18.2s @ 48000Hz. ~36.4s @ 24000Hz
    if audio_file not in cache:
        with open(os.path.join(TEST_DIR, audio_file), "rb") as wavfile:
            cache[audio_file] = wavfile.read()
    mock_translation.raw_audio = cache[audio_file]
    sentence.synthesized_sentences[f"{lang}"] = mock_translation

    return mock_translation


def create_mock_sentence(duration=10, start=0):
    mock_sentence = Sentence(start, start + duration, "x-test", "test")
    return mock_sentence


def test_compressed_file(filename, dtype, mock_sentence, max_allowed_duration):
    # read it back to memory to test for equivalent duration
    with open(f"{TEST_DIR}/{filename}", "rb") as wavfile:
        data, samplerate = sf.read(io.BytesIO(wavfile.read()))

    compressed_duration = data.shape[0] / samplerate

    # After compression, the compressed track must be smaller than
    # max_allowed_duration within floating point error
    return test(
        ((max_allowed_duration - compressed_duration) > -0.1),
        "translation compression",
        f"max_allowed_duration {max_allowed_duration:.1f}, compressed_duration {compressed_duration:0.1f}",
    )


## Perform wav file test
def test_wav_compression(max_allowed_duration):
    # create a sentence with a translation; perform compression
    mock_sentence = create_mock_sentence()
    create_mock_translation(mock_sentence, "test_dub.wav", "test-wav")
    # Testing compression, so pretend this is video
    mock_sentence.post_process_translations(None, max_allowed_duration)
    # save it to disk
    sf.write(
        os.path.join(TEST_DIR, "test_dub_out.wav"),
        mock_sentence.synthesized_sentences["test-wav"].audio,
        48000,
        format="wav",
    )
    return test_compressed_file(
        "test_dub_out.wav", "wav", mock_sentence, max_allowed_duration
    )


def test_raw_compression(max_allowed_duration):
    # create a sentence with a translation; perform compression
    mock_sentence = create_mock_sentence()
    create_mock_translation(mock_sentence, "test_byte_array", "test-raw")
    # Testing compression, so pretend this is video
    mock_sentence.post_process_translations(None, max_allowed_duration)
    # save it to disk
    sf.write(
        os.path.join(TEST_DIR, "test_raw_out.wav"),
        mock_sentence.synthesized_sentences["test-raw"].audio,
        24000,
        format="wav",
    )
    return test_compressed_file(
        "test_raw_out.wav", "raw", mock_sentence, max_allowed_duration
    )


def test_compress_translated_sentences():
    err = 0
    max_allowed_durations = [0.5, 0.99, 1, 3, 6, 10, 18.2, 50, 100]
    for max_allowed_duration in max_allowed_durations:
        err += test_wav_compression(max_allowed_duration)
        err += test_raw_compression(max_allowed_duration)

    return int(err > 3)


def main():
    print("Testing compress translation")
    return test_compress_translated_sentences()


if __name__ == "__main__":
    main()
