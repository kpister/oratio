# This file should be used to test app credentials
# once it runs successfully, you can be sure that
# DeepL translation is set up correctly on this machine
import __init__
from api.translate import deepl_translate as translate
from test_framework import test


def test_translation(client):
    result = translate.get_translation(client, "Hello, there, Let's Play Soccer", "fr")
    return test(result.lower() == "Bonjour à tous, Jouons au football", "translation")


def main():
    err = 0
    print("Test DeepL Translations")
    client = translate.get_client()
    err += test_translation(client)
    print("Translation testing done")
    return err


if __name__ == "__main__":
    main()
