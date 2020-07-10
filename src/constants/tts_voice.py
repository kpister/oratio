# gCloud allows for diffent device profiles for different use cases.
# https://cloud.google.com/text-to-speech/docs/audio-profiles#available_audio_profiles
# headphone-class-device.
from google.cloud.texttospeech import AudioEncoding

GCLOUD_TTS_DEVICE_PROFILE = "large-home-entertainment-class-device"
GCLOUD_DEFAULT_AUDIO_ENCODING = AudioEncoding.LINEAR16

AWS_LANGUAGE_CODES = [
    "arb",
    "cmn-CN",
    "cy-GB",
    "da-DK",
    "de-DE",
    "en-AU",
    "en-GB",
    "en-GB-WLS",
    "en-IN",
    "en-US",
    "es-ES",
    "es-MX",
    "es-US",
    "fr-CA",
    "fr-FR",
    "is-IS",
    "it-IT",
    "ja-JP",
    "hi-IN",
    "ko-KR",
    "nb-NO",
    "nl-NL",
    "pl-PL",
    "pt-BR",
    "pt-PT",
    "ro-RO",
    "ru-RU",
    "sv-SE",
    "tr-TR",
]
