import boto3

from constants.tts_voice import AWS_LANGUAGE_CODES
from target_voice import create_voice


def get_client():
    print("Using AWS for TTS client")
    return boto3.client("polly")


def provider_name():
    return "AWS"


# Input: a JSON object from AWS API containing voice information
# Returns a list of TargetVoices
def normalize_voices(resp):
    voices = []
    for voice in resp:
        # Arabic is 'ar-XA' in gcloud, using gcloud as standard
        if voice["LanguageCode"] == "arb":
            voice["LanguageCode"] = "ar-XA"

        voices.append(
            create_voice(
                locale=voice["LanguageCode"],
                gender=voice["Gender"],
                voiceId=voice["Id"],
            )
        )

    return voices


# Returns a list of aws voice objects in JSON format
def list_voices(client, lang_code=None):
    if lang_code:
        response = client.describe_voices(
            LanguageCode=lang_code, IncludeAdditionalLanguageCodes=True
        )
    else:
        response = client.describe_voices(IncludeAdditionalLanguageCodes=True)

    if "Voices" not in response:
        print("Error parsing voices from AWS TTS")
        return []
    return response["Voices"]


# returns pcm binary stream
# https://en.wikipedia.org/wiki/Pulse-code_modulation
def get_audio_chunk_for_sentence(
    client, text_to_speak, target_voice,
):
    if target_voice.locale not in AWS_LANGUAGE_CODES:
        raise ValueError(f"{target_voice.locale} not supported by AWS for TTS")

    response = client.synthesize_speech(
        VoiceId=target_voice.aws_voice_id,
        LanguageCode=target_voice.locale,
        OutputFormat="ogg_vorbis",
        Text=text_to_speak,
    )

    return response["AudioStream"].read()
