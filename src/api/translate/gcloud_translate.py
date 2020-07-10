import sentence
import six
import os
from google.cloud import translate_v2 as translate
from constants.constants import REPO_PATH


def get_translation(translate_client, text_to_translate, target_language):
    """Translates text into the target language.
    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    if isinstance(text_to_translate, six.binary_type):
        text_to_translate = text_to_translate.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(
        text_to_translate, target_language=target_language
    )
    return result["translatedText"]


# returns a list of all the lang-codes available
def get_supported_languages(translate_client, verbose=False):
    """Lists all available languages for gCloud translate API."""
    results = translate_client.get_languages()
    if verbose:
        for language in results:
            print(u"{name} ({language})".format(**language))
    return [r["language"] for r in results]


# Will first check for keyfile credentials, then use the gcloud utility.
# returns None on failure
def get_client():
    print("Using GCloud for translation client")
    error = []
    try:
        client = translate.Client.from_service_account_json(
            os.path.join(REPO_PATH, ".keyfile.json")
        )
        return client
    except Exception as e:
        error.append(str(e))

    try:
        return translate.Client()
    except Exception as e:
        error.append(str(e))

    print("\n".join(error))
    return None
