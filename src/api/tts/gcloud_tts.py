"""Synthesizes speech from the input string of text or ssml.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from google.cloud import texttospeech
from constants.constants import (
    DEFAULT_AUDIO_OUTPUT_FORMAT,
    REPO_PATH,
)
from constants.tts_voice import (
    GCLOUD_TTS_DEVICE_PROFILE,
    GCLOUD_DEFAULT_AUDIO_ENCODING,
)
import os
from target_voice import create_voice

# returns pcm binary stream
# https://en.wikipedia.org/wiki/Pulse-code_modulation
def get_audio_chunk_for_sentence(
    client,
    text_to_speak,
    target_voice,
    audio_encoding=GCLOUD_DEFAULT_AUDIO_ENCODING,
    speedup=1.0,
):
    # Build the voice request.
    voice = texttospeech.VoiceSelectionParams(
        language_code=target_voice.locale,
        name=target_voice.gcloud_name,
        ssml_gender=target_voice.gender,
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=audio_encoding,
        effects_profile_id=[GCLOUD_TTS_DEVICE_PROFILE],
        speaking_rate=speedup,
    )
    synthesis_input = texttospeech.SynthesisInput(text=text_to_speak)
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    return response.audio_content


def provider_name():
    return "gcloud"


# Input: a JSON object from AWS API containing voice information
# Returns a list of TargetVoices
def normalize_voices(resp):
    voices = []

    resp = sorted(resp.voices, key=lambda x: x.name)
    for voice in resp:
        # We only use Wavenet for now.
        if "Standard" in voice.name:
            print(f"Skipping {voice.name}")
            continue

        voices.append(
            create_voice(
                locale=voice.language_codes[0],
                gender=voice.ssml_gender,
                gcloud_name=voice.name,
            )
        )
    return voices


# Returns a list of gcloud voice objects
def list_voices(client, lang_code=None, verbose=False):
    """Lists the available voices for gCloud TTS."""
    # Performs the list voices request.
    if lang_code:
        voices = client.list_voices(lang_code)
    else:
        voices = client.list_voices()

    if verbose:
        for voice in voices.voices:
            # Display the voice's name. Example: tpc-vocoded
            print(f"Name: {voice.name}")

            # Display the supported language codes for this voice. Example: "en-US"
            for language_code in voice.language_codes:
                print(f"Supported language: {language_code}")

            ssml_gender = texttospeech.SsmlVoiceGender(voice.ssml_gender)

            # Display the SSML Voice Gender
            print(f"SSML Voice Gender: {ssml_gender.name}")

            # Display the natural sample rate hertz for this voice. Example: 24000
            print(f"Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}")
    return voices


# Will first check for keyfile credentials, then use the gcloud utility.
# returns None on failure
def get_client():
    print("Using GCloud for TTS client")
    error = []
    try:
        client = texttospeech.TextToSpeechClient.from_service_account_json(
            os.path.join(REPO_PATH, ".keyfile.json")
        )
        return client
    except Exception as e:
        error.append(str(e))

    try:
        return texttospeech.TextToSpeechClient()
    except Exception as e:
        error.append(str(e))

    print("\n".join(error))
    return None
