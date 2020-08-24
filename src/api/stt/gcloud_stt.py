import os
import math
from google.cloud import speech
from constants.constants import (
    REPO_PATH,
    GCLOUD_UPLOAD_BUCKET_URL,
)
import api.stt.util as util


def _get_stt_config(language_code):

    default_config = {
        "language_code": language_code,
        # sample_rate_hertz is unspecified for flac.
        # "sample_rate_hertz": 48000,
        "encoding": speech.enums.RecognitionConfig.AudioEncoding.FLAC,
        "enable_word_time_offsets": True,
        "enable_automatic_punctuation": True,
        "audio_channel_count": 2,
    }
    if language_code == "en-US":
        default_config["model"] = "video"
        default_config["use_enhanced"] = True
    return default_config


def transcribe_storage_uri(client, uploaded_file, locale):
    config = _get_stt_config(locale)
    storage_uri = os.path.join(GCLOUD_UPLOAD_BUCKET_URL, uploaded_file)
    response = client.long_running_recognize(config, {"uri": storage_uri})
    stt_results = response.result().results
    if len(stt_results) == 0 or len(stt_results[0].alternatives) == 0:
        print("STT found no results and/or alternatives.")
        return []

    return stt_results


# time has .seconds and .nanos
def _get_time_seconds(time):
    """Returns time in seconds rounded to first decimal place."""
    return round(float(time.seconds) + float(time.nanos) * math.pow(10, -9), 1)


def get_word_list(items):
    results = []

    for item in items:
        best_alternative = item.alternatives[0]
        for word in best_alternative.words:
            start = _get_time_seconds(word.start_time)
            end = _get_time_seconds(word.end_time)
            has_punc = util._has_punctuation(word.word)
            if not has_punc:
                results.append(util.Word(word.word, start, end, "normal"))
            else:
                # ASSUMES: punctuation is a single char at end of word
                results.append(util.Word(word.word[:-1], start, end))
                results.append(util.Word(word.word[-1], start, end, is_punc=True))
    return results


# Will first check for keyfile credentials, then use the gcloud utility.
# returns None on failure
def get_client():
    print("Using GCloud for STT client")
    error = []
    try:
        client = speech.SpeechClient.from_service_account_json(
            os.path.join(REPO_PATH, ".keyfile.json")
        )
        return client
    except Exception as e:
        error.append(str(e))

    try:
        return speech.SpeechClient()
    except Exception as e:
        error.append(str(e))

    print("\n".join(error))
    return None
