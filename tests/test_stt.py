import os
import __init__

from test_framework import test
from api.stt import gcloud_stt as stt
from constants.constants import REPO_PATH, TEST_DIR


def test_connection(client):
    pass


def test_transcription(client, stream):
    pass


def main():
    print("Testing Speech to Text")
    client = stt.get_client()
    test_connection(client)
    test_transcription(client, stream)
    print("Speech to Text testing done")
    return 0


if __name__ == "__main__":
    main()
