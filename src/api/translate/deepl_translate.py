# deepl translate
import six
import requests
from constants.constants import DEEPL_API_KEY


def get_translation(text_to_translate, target_language):
    """Translates text into the target language.
    Target must be an ISO 639-1 language code.
    See https://www.deepl.com/docs-api/other-functions/listing-supported-languages/
    """
    if isinstance(text_to_translate, six.binary_type):
        text_to_translate = text_to_translate.decode("utf-8")

    translated_lst, error = [], []
    # List of required parameters for response.
    try:
        parameters = {
            "text": text_to_translate,
            "target_lang": target_language,
            "auth_key": DEEPL_API_KEY,
        }
        # making request to deepl translation API.
        # returns a JSON representation of the translation in the order the text parameters have been specified.
        response = requests.get("https://api.deepl.com/v2/translate", params=parameters)
        responses = response.json()
        for item in responses.values():
            for key in item:
                translated_lst.append(key["text"])
    except Exception as e:
        error.append(str(e))

    print("\n".join(error))

    print(responses)
    return translated_lst[0]
