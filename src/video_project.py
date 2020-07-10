import os
import overlay
import project
import track

from moviepy.editor import VideoFileClip, AudioFileClip
from constants.constants import (
    DUBBED_AUDIO_FILENAME,
    DUBBED_COMPOSITE_FILENAME,
    DEFAULT_CODEC_FOR_DUBBED_VIDEO,
)


class VideoProject(project.Project):
    def __init__(self, config):
        super().__init__(config)
        assert config.is_video()

        self.video_clip = VideoFileClip(config.input_media_path)
        self.original_video_length = round(self.video_clip.duration, 1)
        self.audio_clip = self.video_clip.audio
        self.save_original_audio_as_flac()
        self.include_watermarks = config.include_watermarks

        # use a rotation of languages like the beckham malaria video
        # https://www.youtube.com/watch?v=U-mg7a1vwkw
        self.produce_beckham = config.beckham
        if self.produce_beckham:
            # For beckham video each sentence is tagged to an output locale.
            self.beckham_sentence_to_locale_map = {}
            self.sentences_per_locale = config.beckham_rotation_speed

    def _intialize_beckham(self):
        # Number of consecutive sentences before the language switches.
        # Switch language after each sentence to show robustness.
        all_locales = self.target_locales + [self.input_locale]
        for idx, sentence in enumerate(self.sentences):
            self.beckham_sentence_to_locale_map[sentence] = all_locales[
                int((idx / self.sentences_per_locale) % len(all_locales))
            ]

    def _get_locale_duration_tuples(self, target_locale, dubbed_video):
        if target_locale != "beckham":
            # Single language dubbing.
            return [(target_locale, dubbed_video.duration)]

        if not self.sentences:
            return [(target_locale, 0)]
        locale_durations = []

        # Duration for sentenceN = sentenceN+1.start_time - sentenceN.start_time
        for idx in range(len(self.sentences) - 1):
            curr_sentence = self.sentences[idx]
            next_sentence = self.sentences[idx + 1]
            if idx == 0:
                # First sentence. Some 1st sentence start at t > 0.
                locale_durations.append(
                    (
                        self.beckham_sentence_to_locale_map[curr_sentence],
                        next_sentence.start_time,
                    )
                )
            else:
                locale_durations.append(
                    (
                        self.beckham_sentence_to_locale_map[curr_sentence],
                        next_sentence.start_time - curr_sentence.start_time,
                    )
                )

        # Last sentence. Use dubbed_video.length to get duration.
        last_sentence = self.sentences[-1]
        locale_durations.append(
            (
                self.beckham_sentence_to_locale_map[last_sentence],
                dubbed_video.duration - last_sentence.start_time,
            )
        )

        return locale_durations

    def _locales_to_export(self):
        # If beckham is set, only save the beckham video to disk.
        if self.produce_beckham:
            return ["beckham"]
        return self.target_locales

    def _fps(self):
        if self.config.export_fps:
            print(f"WARNING! Using a fps value = {self.config.export_fps}.")
            return self.config.export_fps
        return self.video_clip.fps

    # create a new mp4 version of the video for each translation available.
    def overlay_dubbing_and_save(self):
        for locale in self._locales_to_export():
            track = self.tracks[locale]
            dubbed_audio = AudioFileClip(
                os.path.join(self.full_path, locale, DUBBED_AUDIO_FILENAME)
            )
            dubbed_video = self.video_clip.set_audio(dubbed_audio)

            if self.include_watermarks:
                translated_locale_durations = self._get_locale_duration_tuples(
                    locale, dubbed_video
                )
                dubbed_video = overlay.watermark_video_clip(
                    dubbed_video, self.input_locale, translated_locale_durations
                )

            dubbed_video.write_videofile(
                os.path.join(
                    self.full_path, locale, f"{locale}_{DUBBED_COMPOSITE_FILENAME}"
                ),
                # TODO; This should be only used for .mov exports.
                # For .mp4 .ogv and .webm, codec is set automatically.
                codec=DEFAULT_CODEC_FOR_DUBBED_VIDEO,
                fps=self._fps(),
            )

    # Forces all translations to match original sentence start_times
    def process_translated_audio(self):
        for idx, sentence in enumerate(self.sentences):
            # Dubbed audio can extend up to the end of the video
            if idx == (len(self.sentences) - 1):
                end = self.original_video_length
            # Dubbed audio can extend up to start of next sentence
            else:
                end = self.sentences[idx + 1].start_time

            max_allowed_duration = end - sentence.start_time

            sentence.post_process_translations(self.client, max_allowed_duration)

    def generate_tracks(self):
        if self.produce_beckham:
            self._intialize_beckham()
            self.generate_beckham_track()
        else:
            super().generate_tracks()

            # make sure each track is the same duration as the original video
            # important edge case: translation is longer (handled in add_blank)
            for locale in self.target_locales:
                self.tracks[locale].add_blank(self.original_video_length)

    # still need to save tracks after this call
    def generate_beckham_track(self):
        beckham_track = track.Track("beckham")
        for sentence in self.sentences:
            target_locale = self.beckham_sentence_to_locale_map[sentence]
            beckham_track.concat(
                "beckham",
                sentence.synthesized_sentences[target_locale],
                sentence.start_time,
                True,
            )
        self.tracks["beckham"] = beckham_track

    def _add_sentence_to_track(self, sentence):
        for locale in self.target_locales + [self.input_locale]:
            translation = sentence.synthesized_sentences[locale]

            self.tracks[locale].concat(
                locale, translation, sentence.start_time, True,
            )
