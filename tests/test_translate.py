# This file should be used to test app credentials
# once it runs successfully, you can be sure that
# google cloud is set up correctly on this machine

import __init__
from api.translate import gcloud_translate as translate
from test_framework import test


def test_connection(client):
    # test that we have many languages
    results = translate.get_supported_languages(client)
    return test((results is not None and results != []), "available languages")


def test_translation(client):
    result = translate.get_translation(client, "Hello world", "es")
    return test(result.lower() == "hola mundo", "translation")


def main():
    err = 0
    print("Test translation")
    client = translate.get_client()
    err += test_connection(client)
    err += test_translation(client)
    print("Translation testing done")
    return err


if __name__ == "__main__":
    main()
