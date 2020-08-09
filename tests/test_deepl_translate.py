# This file should be used to test app credentials
# once it runs successfully, you can be sure that
# AWS with DeepL translation is set up correctly on this machine
import __init__
from api.translate import deepl_translate as translate
from test_framework import test


def test_translation():
    result = translate.get_translation("Hello, there, Let's Play Soccer", "fr")
    return test(result == "Bonjour à tous, Jouons au football", "translation")


def main():
    err = 0
    print("Test DeepL Translations")
    err += test_translation()
    print("Translation testing Done")

    return err


if __name__ == "__main__":
    main()
