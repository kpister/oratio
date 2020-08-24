import io
import soundfile as sf
import numpy
import pyrubberband
from html import unescape

from target_voice import get_lang_code

# This will not work without the rubberband library: https://breakfastquay.com/rubberband/index.html
# brew install rubberband on macOS


class Sentence:
    def __init__(
        self, start_time, end_time, input_locale, original_text, speaker = 1, gender = 1
    ):
        self.start_time = start_time
        self.end_time = end_time
        self.input_locale = input_locale
        self.original_text = original_text
        self.speaker = speaker
        self.gender = gender  # note that sentence genders are stored as ints not strings
        self.duration = round(end_time - start_time, 1)
        # Map of (target_language,TranslatedSentence)
        self.translated_sentences = {}
        self.translated_sentences[get_lang_code(input_locale)] = TranslatedSentence(
            get_lang_code(input_locale), original_text
        )

        # Map of (target_locale,SynthesizedSentence)
        self.synthesized_sentences = {}

    def __str__(self):
        return str(self.to_dict())

    # Used to save sentences to disk after transcription.
    def to_dict(self):
        return {
            "speaker": self.speaker,
            "gender": self.gender,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "original_text": self.original_text,
            "translated_sentences": [
                t.to_dict() for _, t in self.translated_sentences.items()
            ],
        }

    def post_process_translations(self, client=None, max_allowed_duration=0):
        for locale, translation in self.synthesized_sentences.items():
            if locale == self.input_locale:
                continue

            audio_bytes, samplerate = sf.read(
                io.BytesIO(translation.raw_audio), always_2d=True
            )
            translation.raw_audio = audio_bytes
            translation.samplerate = samplerate
            # max_allowed_duration is only used on video dubbing
            if max_allowed_duration > 0:
                self.compress_translated_sentence(
                    translation, max_allowed_duration, locale, client
                )
            else:
                translation.audio = translation.raw_audio

    # compress translated_sentences in self.translated_sentences if needed.
    # end state: each translated_sentence end before the start of next
    # translated_sentence.
    # start_time for each translated_sentences is same
    # Assumes:
    #   self.translated_sentences is a dictionary of lang: byte stream
    #   rubberband is installed in addition to pyrubberband
    def compress_translated_sentence(
        self, translation, max_allowed_duration, locale, client
    ):

        audio_bytes = translation.raw_audio
        samplerate = translation.samplerate

        # duration = frames / samplerate
        translation.compression_ratio = float(
            (audio_bytes.shape[0] / samplerate)
        ) / float(max_allowed_duration)

        if client and client.gcloud_speedup and translation.compression_ratio > 1.0:
            audio_bytes, samplerate = sf.read(
                io.BytesIO(
                    client.get_audio_chunk_for_sentence(
                        translation.text, locale, self.speaker, self.gender, speedup=translation.compression_ratio
                    )
                ),
                always_2d=True,
            )

            # we might be slightly off on timing here. Gcloud isn't perfect
            # recalc the compression
            translation.compression_ratio = float(
                (audio_bytes.shape[0] / samplerate)
            ) / float(max_allowed_duration)

        if translation.compression_ratio > 1.0:
            audio_bytes = pyrubberband.time_stretch(
                audio_bytes, samplerate, translation.compression_ratio
            )
        translation.audio = audio_bytes

    def get_translated_sentence(self, locale):
        lang_code = get_lang_code(locale)
        return self.translated_sentences[lang_code]

    # Translate this sentence into each of its target locales.
    # Translate APIs uses two letter language codes.
    def translate(self, client, lang_code):
        # the lang_code here still needs conversion from cmn to zh for example
        target_language = get_lang_code(lang_code)
        raw_translation = client.get_translation(
            unescape(self.original_text), target_language
        )
        # Languages like french have apostrophes.
        # gCloud translate uses HTML character references.
        self.translated_sentences[lang_code] = TranslatedSentence(
            lang_code, unescape(raw_translation)
        )

    # Use Text to Speech to translate this sentence into each of its target voices
    def synthesize(self, client, locale):
        translation = self.get_translated_sentence(locale)
        translated_audio = client.get_audio_chunk_for_sentence(translation.text, locale, self.speaker, self.gender)
        self.synthesized_sentences[locale] = SynthesizedSentence(
            locale, translated_audio, text=translation.text
        )


class TranslatedSentence:
    def __init__(self, lang_code, translated_text):
        self.lang_code = lang_code
        self.text = translated_text

    def to_dict(self):
        return {
            "lang_code": self.lang_code,
            "text": self.text,
        }

    def __str__(self):
        return str(self.to_dict())


class SynthesizedSentence:
    def __init__(self, locale, raw_audio=None, audio=None, samplerate=None, text=None):
        self.locale = locale
        # Byte array received from gCloud TTS API.
        self.raw_audio = raw_audio
        self.audio = audio
        self.compression_ratio = None
        self.samplerate = samplerate
        self.text = text

    # Always calcualted on final audio, i.e. post-audio compression/
    def get_audio_duration(self):
        return self.audio.shape[0] / self.samplerate
