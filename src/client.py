import enum
import json
from target_voice import create_voice, gender_string, gender_number
import api.stt.util


class Provider(enum.Enum):
    GCLOUD = 1
    AWS = 2
    IBM = 3


class Client:
    def __init__(
        self,
        upload_filename,
        stt_provider=Provider.GCLOUD,
        translate_provider=Provider.GCLOUD,
        tts_provider=Provider.GCLOUD,
        gcloud_speedup=False,  # temporary flag
    ):
        self.upload_filename = upload_filename
        self.stt_provider = stt_provider
        self.translate_provider = translate_provider
        self.tts_provider = tts_provider
        self.setup_clients()
        self.gcloud_speedup = gcloud_speedup

    def setup_clients(self):
        if self.stt_provider == Provider.GCLOUD:
            from api.storage import gcloud_storage as storage
            from api.stt import gcloud_stt as stt
        if self.translate_provider == Provider.GCLOUD:
            from api.translate import gcloud_translate as translate
        if self.tts_provider == Provider.GCLOUD:
            from api.tts import gcloud_tts as tts

        if self.stt_provider == Provider.AWS:
            from api.storage import aws_storage as storage
            from api.stt import aws_stt as stt
        if self.translate_provider == Provider.AWS:
            from api.translate import aws_translate as translate
        if self.tts_provider == Provider.AWS:
            from api.tts import aws_tts as tts

        if self.translate_provider == Provider.IBM:
            from api.translate import ibm_translate as translate

        self.storage = storage
        self.stt = stt
        self.translate = translate
        self.tts = tts

        self.storage_client = storage.get_client()
        self.stt_client = stt.get_client()
        self.translate_client = translate.get_client()
        self.tts_client = tts.get_client()

        self.target_voices = {}

    # input_file should be a complete path
    def upload_file_to_cloud(self, input_file):
        self.storage.upload_file_to_cloud(
            self.storage_client, input_file, self.upload_filename
        )

    def transcribe_sentences(self, locale):
        response = self.stt.transcribe_storage_uri(
            self.stt_client, self.upload_filename, locale
        )
        word_list = self.stt.get_word_list(response)

        return api.stt.util.create_sentences_from_word_list(word_list, locale)

    def get_translation(self, original_text, target_language):
        return self.translate.get_translation(
            self.translate_client, original_text, target_language
        )

    def get_target_voice(self, locale, gender, speaker):
        response = self.tts.list_voices(self.tts_client, locale)
        voices = self.tts.normalize_voices(response)

        # find the best matches
        options = [
            v for v in voices if (v.locale == locale and v.gender == gender)
        ]

        if voices == []:
            # TODO add error handling
            return None

        if options == []:
            print("Couldn't find a matching voice.")
            return voices[0]

        # if there is only one option, there is no option
        if len(options) == 1:
            return options[0]

        print(f"Speaker #{speaker}")
        print(f"Options for {locale}")
        for idx, voice in enumerate(options):
            print(f"#{idx} - {voice.name}")

        choice = input(
            f"Choose a voice by entering a number between 0:{len(options)-1} [Default: 0]: "
        )
        if choice.strip() == "":
            choice = 0

        return options[int(choice)]

    def get_audio_chunk_for_sentence(self, text, locale, speaker, gender, speedup=1.0):
        if (locale+str(speaker)) not in self.target_voices:
            self.target_voices[locale+str(speaker)] = self.get_target_voice(locale, gender, speaker)
            print(self.target_voices[locale+str(speaker)])
            update_best_voices = input(
                "Would you like to update the best voices file? (y/N) "
            )
            if update_best_voices == "y":
                self.save_best_voices(speaker, gender)

        return self.tts.get_audio_chunk_for_sentence(
            self.tts_client, text, self.target_voices[locale+str(speaker)], speedup=speedup
        )

    # Returns a list of voices
    def get_all_matching_voices(self):
        response = self.tts.list_voices(self.tts_client)
        voices = self.tts.normalize_voices(response)

        translation_lang_codes = self.translate.get_supported_languages(
            self.translate_client
        )

        # don't synthesize if the translation doesn't exist
        broken = []
        for v in voices:
            if v.lang_code not in translation_lang_codes:
                broken.append(v.locale)

        return [
            v for v in voices if (v.locale not in broken)
        ]

    def load_best_voices(self, voices_file, target_locales):
        # json will have the following structure
        # dict follows this structure -> voices[platform][speaker][speaker_data]
        # {
        #   "gcloud": {
        #       "1": {
        #           "gender": "male",
        #           "locale": "en-GB",
        #           "voice_name": "en-GB-Wavenet-B"
        #       }
        #   }
        #   "AWS" : {
        #       "1": {
        #           "gender": "male",
        #           "locale": "en-GB",
        #           "voice_name": "..."
        #       }
        #   }
        # }
        self.voices_file = voices_file
        with open(voices_file) as f:
            voices = json.load(f)

        provider = self.tts.provider_name()
        if provider not in voices:
            return

        for speaker, speaker_data in voices[
            provider
        ].items():
            speaker = int(speaker)
            gender = speaker_data["gender"]
            locale = speaker_data["locale"]
            voice_name = speaker_data["voice_name"]
            if provider == "AWS":
                self.target_voices[locale+str(speaker)] = create_voice(
                    locale, gender, voiceId=voice_name
                )
            if provider == "gcloud":
                self.target_voices[locale+str(speaker)] = create_voice(
                    locale, gender, gcloud_name=voice_name
                )
            if locale in target_locales:
                print(self.target_voices[locale+str(speaker)])

    def save_best_voices(self, speaker, gender):
        with open(self.voices_file) as f:
            voices = json.load(f)

        provider = self.tts.provider_name()

        if provider not in voices:
            voices[provider] = {}

        if speaker not in voices[provider]:
            voices[provider][speaker] = {}

        for locale_and_speaker, voice in self.target_voices.items():
            gender = gender_string(gender)  # converts gender number to string
            locale = locale_and_speaker[:-1]  # extracts locale from target_voices dict key
            voice_name = voice.name  # extracts voice's name from the voice name value
            voices[provider][speaker]["gender"] = gender
            voices[provider][speaker]["locale"] = locale
            voices[provider][speaker]["voice_name"] = voice_name

        with open(self.voices_file, "w") as w:
            w.write(json.dumps(voices, indent=2))
