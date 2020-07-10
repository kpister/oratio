import __init__
from test_framework import test
from constants.tts_voice import GCLOUD_SPANISH_FEMALE


def test_connection(tts, client):
    results = tts.list_voices(client, "fr-FR")
    voices = tts.normalize_voices(results)
    return test(results is not None and results != [], "synthesis connection")


def test_synthesis(tts, client):
    results = tts.list_voices(client, "fr-FR")
    voices = tts.normalize_voices(results)
    result = tts.get_audio_chunk_for_sentence(client, "hola mundo", voices[0])


def test_tts(tts):
    err = 0
    print("Testing Text to Speech")
    client = tts.get_client()
    err += test_connection(tts, client)
    test_synthesis(tts, client)
    print("Text to Speech testing done")
    return err


def main():
    err = 0
    from api.tts import gcloud_tts as tts

    err += test_tts(tts)

    from api.tts import aws_tts as tts

    err += test_tts(tts)
    return err


if __name__ == "__main__":
    main()
