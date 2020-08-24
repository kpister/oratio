import numpy
import io
import json
import os
import overlay
import soundfile as sf

from client import Client

from constants.constants import (
    TRANSCRIBED_SENTENCES_FILENAME,
    TRANSLATED_SENTENCES_FILENAME,
    DUBBED_AUDIO_FILENAME,
    DEFAULT_STT_INPUT_FILENAME,
    DEFAULT_STT_INPUT_FORMAT,
    REPO_PATH,
    PY_AUDIO_ANALYSIS_DATA_DIRECTORY,
    SentenceIoMode,
)
from moviepy.editor import VideoFileClip, AudioFileClip
from sentence import Sentence, TranslatedSentence, SynthesizedSentence
from track import Track

# A project contains the original work as well as a collection of tracks
class Project:
    # Serves as a collection of sentences
    # provides methods which operate on all the sentences of a file
    def __init__(self, config):
        self.config = config

        self.input_locale = config.input_locale
        self.input_language = config.input_language
        self.target_locales = config.target_locales
        self.target_languages = config.target_languages
        # Production path contains final videos and audio
        self.full_path = config.prod_path
        # Dev path contains in between audio segments and transcriptions
        self.dev_path = config.dev_path
        self.client = config.client

        self.num_of_speakers = config.num_of_speakers
        self.speaker_genders = {}

        self.sentences = []
        self.tracks = {}

        if not config.is_video():
            self.audio_clip = AudioFileClip(
                os.path.join(config.prod_path, config.input_media_file)
            )
            self.save_original_audio_as_flac()

        if config.use_background_music:
            self.background_music, self.background_samplerate = sf.read(
                config.background_music_path, always_2d=True
            )

        if config.use_best_voices:
            self.client.load_best_voices(config.best_voices_path, self.target_locales)

    ##### Functions to save/load project on disk #####

    # Save the audio as a flac for STT, always use the same default name
    def save_original_audio_as_flac(self):
        filename = os.path.join(
            self.full_path, (DEFAULT_STT_INPUT_FILENAME + DEFAULT_STT_INPUT_FORMAT)
        )
        # don't overwrite a previous flac
        if not os.path.isfile(filename):
            self.audio_clip.write_audiofile(filename, codec="flac")

    # Used to write the transcribed sentences to temporary storage for review
    def save_sentences(self, mode):
        filename = self._get_sentence_filename(mode)
        export_dict = {"sentences": [s.to_dict() for s in self.sentences]}
        with open(os.path.join(self.config.dev_path, filename), "w") as f:
            f.write(json.dumps(export_dict, indent=2))

    def load_sentences(self, mode):
        filename = self._get_sentence_filename(mode)
        self.sentences = []  # clear sentences since we will reload it

        with open(os.path.join(self.dev_path, filename)) as f:
            data = json.load(f)

        for row in data["sentences"]:
            sentence = Sentence(
                row["start_time"],
                row["end_time"],
                self.input_locale,
                row["original_text"],
                row["speaker"],
                row["gender"]
            )
            if mode == SentenceIoMode.TRANSLATE:
                for translation in row["translated_sentences"]:
                    if translation["lang_code"] not in (
                        self.target_languages + [self.input_language]
                    ):
                        continue

                    sentence.translated_sentences[
                        translation["lang_code"]
                    ] = TranslatedSentence(
                        translation["lang_code"], translation["text"]
                    )
            self.sentences.append(sentence)

        # validate sentence start_times
        prev_sentence_start = 0
        for idx, sentence in enumerate(self.sentences):
            if sentence.start_time <= prev_sentence_start:
                raise ValueError(
                    f"Sentence {idx} has an invalid start time (it starts too soon)"
                )
            prev_sentence_start = sentence.start_time

    # saves a wav file for each tts sentence (used for debugging, etc.)
    def save_audio_sentences(self):
        for idx, sentence in enumerate(self.sentences):
            for locale in self.target_locales + [self.input_locale]:
                translation = sentence.synthesized_sentences[locale]
                filename = os.path.join(self.dev_path, locale, f"sentence_{idx}.wav")
                sf.write(
                    filename, translation.audio, translation.samplerate, format="wav",
                )

    # loads a wav file for each tts sentence (used for debugging, etc.)
    # this could be done more automatically (don't require sentences to be full)
    def load_audio_sentences(self):
        for idx, sentence in enumerate(self.sentences):
            for locale in self.target_locales + [self.input_locale]:
                filename = os.path.join(self.dev_path, locale, f"sentence_{idx}.wav")
                with open(filename, "rb") as f:
                    audio_bytes, samplerate = sf.read(
                        io.BytesIO(f.read()), always_2d=True
                    )
                sentence.synthesized_sentences[locale] = SynthesizedSentence(
                    locale, audio=audio_bytes, samplerate=samplerate
                )

    # Saves the project to disk in as many .wav files as languages
    # uses self.tracks to build each language file
    def generate_tracks(self):
        assert len(self.sentences) > 0
        # initialize each language track
        self.tracks = {locale: Track(locale) for locale in self.target_locales}
        self.tracks[self.input_locale] = Track(self.input_locale)

        # save a concatenation of all the sentences in all languages to disk
        for idx, sentence in enumerate(self.sentences):
            self._add_sentence_to_track(sentence)

    def save_tracks(self):
        for locale, track in self.tracks.items():
            track.stack()
            if self.config.use_background_music:
                track.add_background_music(
                    self.background_music, self.background_samplerate
                )

            if self.config.use_original_bg:
                track.add_background_music(
                    self.original_audio_null_mask, self.original_audio_samplerate
                )

            filename = os.path.join(self.full_path, locale, DUBBED_AUDIO_FILENAME)
            sf.write(filename, track.audio, track.samplerate, format="wav")

    ##### Functions on the project sentences #####

    # Uploads default flac file that was generated from save_original_audio_as_flac
    def upload_flac_to_cloud_bucket(self):
        self.client.upload_file_to_cloud(
            os.path.join(
                self.full_path, (DEFAULT_STT_INPUT_FILENAME + DEFAULT_STT_INPUT_FORMAT)
            )
        )

    def diarize_sentences(self):
        if self.num_of_speakers != 1:
            from pyAudioAnalysis.audioSegmentation import speaker_diarization

            input_file = os.path.join(
                self.full_path, (DEFAULT_STT_INPUT_FILENAME + DEFAULT_STT_INPUT_FORMAT)
            )
            output_file = os.path.join(
                REPO_PATH, PY_AUDIO_ANALYSIS_DATA_DIRECTORY, (DEFAULT_STT_INPUT_FILENAME + ".wav")
            )
            command = "ffmpeg -i " + input_file + " " + output_file
            os.system(command)
            input("\a\nFFmpeg audio conversion for diarization complete. Press <enter> to continue")

            diarized_speakers = speaker_diarization(output_file, self.num_of_speakers)
            input("\a\nDiarization complete. Press <enter> to continue")

            # list of speakers... example -> [0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0]
            diarized_speakers.tolist()  # converts from numpy ndarray
            # the number of speakers in the audio/video (this could have been dynamically determined)
            self.num_of_speakers = int(max(diarized_speakers) + 1)
            # sometimes the ML algo doesn't mark the original speaker as 0... this corrects that
            # by moving every speaker marker down by one (zeros circle back to the top)
            if int(diarized_speakers[0]) != 0:
                for i in range(len(diarized_speakers)):
                    if diarized_speakers[int(i)] > 0:
                        diarized_speakers[int(i)] -= 1
                    elif diarized_speakers[int(i)] == 0:
                        diarized_speakers[int(i)] = self.num_of_speakers - 1
            # parallel list to diarized_speakers; the time of each element in diarized_speakers
            speaker_timing = [round((i*0.2+0.1), 1) for i in range(len(diarized_speakers))]

            print(f"\a\n{self.num_of_speakers} unique speakers detected:")
            for i in range(self.num_of_speakers):
                self.speaker_genders[(i+1)] = input(f"\tSpeaker #{(i+1)} gender (male=1, female=2, unknown=3): ")

            for sentence in self.sentences:
                # finds sub list of valid speakers inside time interval of sentence
                start = sentence.start_time
                end = sentence.end_time
                valid_times = [time for time in speaker_timing if time >= start if time <= end]
                valid_speakers = [diarized_speakers[speaker_timing.index(time)] for time in valid_times]
                # sets sentence's speaker and gender based on the most prevelant speaker in the interval
                sentence.speaker = int(max(set(valid_speakers), key = valid_speakers.count)) + 1
                sentence.gender = int(self.speaker_genders[sentence.speaker])

    def verify_diarization(self):
        if self.num_of_speakers != 1:
            if input("Is diarization verification needed? [y/N] ") == "y":
                for sentence in self.sentences:
                    print(f"Diarization determined speaker #{sentence.speaker} said \"{sentence.original_text}\"")
                    real_speaker = int(input("\tWho really said this? "))
                    if real_speaker <= self.num_of_speakers and real_speaker > 0:
                        sentence.speaker = real_speaker
                        sentence.gender = int(self.speaker_genders[sentence.speaker])
                    elif real_speaker > self.num_of_speakers or real_speaker <= 0:
                        print("Invalid input; ignoring")

    def transcribe_sentences(self):
        self.sentences = self.client.transcribe_sentences(self.input_locale)

    # translate all sentences into all languages
    def translate_sentences(self):
        # only translate to each lang_code once
        for lang_code in self.target_languages:
            for sentence in self.sentences:
                sentence.translate(self.client, lang_code)
            print(f"Translation for {lang_code} completed")

    # synthesize all sentences into all voices
    def synthesize_voices(self):
        for locale in self.target_locales:
            for sentence in self.sentences:
                sentence.synthesize(self.client, locale)
            print(f"Synthesis for {locale} completed")

        # load it back in as flac to use for original synthesized_sentence
        filename = os.path.join(
            self.full_path, (DEFAULT_STT_INPUT_FILENAME + DEFAULT_STT_INPUT_FORMAT)
        )
        with open(filename, "rb") as f:
            flac_audio, flac_sr = sf.read(io.BytesIO(f.read()), always_2d=True)

        for sentence in self.sentences:
            original_sentence_audio = flac_audio[
                int(sentence.start_time * flac_sr) : int(sentence.end_time * flac_sr), :
            ]
            sentence.synthesized_sentences[self.input_locale] = SynthesizedSentence(
                self.input_locale, audio=original_sentence_audio, samplerate=flac_sr
            )

    # Forces all translations to match original sentence durations for video
    # dubbings.
    def process_translated_audio(self):
        [s.post_process_translations() for s in self.sentences]

    def create_original_audio_mask(self):
        filename = os.path.join(
            self.full_path, (DEFAULT_STT_INPUT_FILENAME + DEFAULT_STT_INPUT_FORMAT)
        )

        with open(filename, "rb") as f:
            audio_bytes, samplerate = sf.read(io.BytesIO(f.read()), always_2d=True)
            self.original_audio_samplerate = samplerate

        mask = [1 for _ in range(audio_bytes.shape[0])]
        prev_end = 0
        start = 1
        for sentence in self.sentences:
            if sentence.start_time < (prev_end + 10):
                start = 0
            else:
                start = 1

            b = int(sentence.start_time * samplerate)
            e = int(sentence.end_time * samplerate)
            prev_end = sentence.end_time
            steps = e - b
            for i in range(b, e):
                vol = min(1 - (5 * (i - b) // steps), start)
                mask[i] = min(0.7, max(0.05, vol))

        self.original_audio_null_mask = audio_bytes * numpy.stack([mask, mask], axis=1)

    # returns a numpy array which represents the volume of the original audio
    # the goal is a whisper in the original, will translate to whisper in dub
    # TODO; this function is a stub, and needs to be tests/researched
    def create_original_volume_mask(self):
        segments = []
        for segment in self.tracks[self.input_locale].segments:
            #   decibel, root mean square, full scale [https://en.wikipedia.org/wiki/DBFS]
            db_rms_fs = numpy.log10(numpy.sqrt(numpy.mean(segment ** 2)))
            segments.append(db_rms_fs)
        import pdb

        pdb.set_trace()
        return numpy.vstack(tuple([i for i in segments]))

    ##### Helper functions #####

    # Transcriptions and Translations are saved separately
    # used by save_sentences and load_sentences
    def _get_sentence_filename(self, mode):
        if mode == SentenceIoMode.TRANSCRIBE:
            return TRANSCRIBED_SENTENCES_FILENAME
        elif mode == SentenceIoMode.TRANSLATE:
            return TRANSLATED_SENTENCES_FILENAME
        else:
            raise ValueError("mode should be either TRANSCRIBE or TRANSLATE")

    # Add one sentence at a time
    # used by save_audio_translations
    def _add_sentence_to_track(self, sentence):
        for locale in self.target_locales + [self.input_locale]:
            translation = sentence.synthesized_sentences[locale]
            self.tracks[locale].concat(
                locale, translation, sentence.start_time, False,
            )
