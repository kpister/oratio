import os
import json
import six
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ApiException as IBMException
from constants.constants import REPO_PATH


def get_translation(translate_client, text_to_translate, target_language):
    """Translates text into the target language.
    Target must be an ISO 639-1 language code.
    See https://cloud.ibm.com/docs/language-translator?topic=language-translator-translation-models
    """
    if isinstance(text_to_translate, six.binary_type):
        text_to_translate = text_to_translate.decode("utf-8")

    results = translate_client.translate(
        text=text_to_translate,
        target=target_language).get_result()
    # example results: {'translations': [{'translation': 'Sono assolutamente sconvolto questo in realtà funziona!'}], 'word_count': 8, 'character_count': 41}

    return results['translations'][0]['translation']


def get_supported_languages(translate_client, verbose=False):
    """Lists all available ~identifiable~ languages for IBM Watson translation API."""
    identifiable_languages = translate_client.list_identifiable_languages().get_result()
    # example identifiable_languages: {'languages': [{'language': 'af', 'name': 'Afrikaans'}, {'language': 'ar', 'name': 'Arabic'}, ... ] }
    results = identifiable_languages['languages']
    if verbose:
        for language in results:
            print(u"{name} ({language})".format(**language))
    return results


def get_client():
    print("Using IBM Watson for translation client")
    error = []
    try:
        # reads the API key and url from the IBM json
        with open(os.path.join(REPO_PATH, ".ibmkeyfile.json")) as f:
            results = json.load(f)
            api_key = results["api_key"]
            api_url = results["api_url"]

        # instantiates instance of IBM API with IAM authentication
        authenticator = IAMAuthenticator(api_key)
        language_translator = LanguageTranslatorV3(
            version='2018-05-01', # this is the current version
            authenticator=authenticator
        )
        language_translator.set_service_url(api_url)

        return language_translator

    except IBMException as e:
        error.append(str(e))

    except Exception as e:
        error.append(str(e))

    print("\n".join(error))
    return None
