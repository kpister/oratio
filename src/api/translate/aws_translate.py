import six
import boto3

def get_client():
    print("Using AWS for translation client")
    return boto3.client("translate")


def get_translation(translate_client, text_to_translate, target_language):
    """Translates text into the target language.
    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    if isinstance(text_to_translate, six.binary_type):
        text_to_translate = text_to_translate.decode("utf-8")

    result = translate_client.translate_text(Text=text_to_translate,
        SourceLanguageCode="auto", TargetLanguageCode=target_language)

    print(result)
    return result["TranslatedText"]
