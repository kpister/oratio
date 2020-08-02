import numpy
import math
from librosa import resample

from constants.constants import (
    MAX_PODCAST_SILENCE_DURATION,
    BACKGROUND_MUSIC_INTENSITY,
)

# Track serves as a collection of sentences in a single language.
# Each track should translate to one translation
class Track:
    def __init__(self, locale, samplerate=None):
        # A single language, should represent one output file
        self.audio = None
        self.locale = locale
        self.samplerate = samplerate
        self.segments = []
        # Moving pointer which tracks the last added audio and silence.
        self.current_end_time = 0
        self.bg_music = None
        self.shape = None

    # Add background audio to the track. Can only be called after a track has been stacked
    def add_background_music(self, bg_bytes, bg_samplerate):
        assert self.audio is not None, "Track is not stacked"

        # Two mismatches are going to be present: Sample rate and duration
        # fix samplerate
        if bg_samplerate != self.samplerate:
            bg_bytes = resample(
                numpy.asfortranarray(bg_bytes[:, 0]), bg_samplerate, self.samplerate
            )

            # 2 channel audio
            if self.audio.shape[1] == 2:
                bg_bytes = numpy.stack([bg_bytes, bg_bytes], axis=1)
            # 1 channel audio
            else:
                bg_bytes = numpy.expand_dims(bg_bytes, axis=1)

        # fix duration
        if bg_bytes.shape[0] != self.audio.shape[0]:
            bg_bytes = fix_shape(bg_bytes, self.audio.shape[0])

        if self.bg_music is None:
            self.bg_music = BACKGROUND_MUSIC_INTENSITY * bg_bytes

        self.audio += self.bg_music

    def concat(self, locale, segment, start_time, is_video):
        if self.samplerate is None:
            self.samplerate = segment.samplerate

        # this is only used for original audio, but could be relevant for different providers
        if segment.samplerate != self.samplerate:
            resampled_audio = resample(
                numpy.asfortranarray(segment.audio[:, 0]),
                segment.samplerate,
                self.samplerate,
            )
            segment.audio = numpy.expand_dims(resampled_audio, axis=1)

        assert self.locale == locale

        # Determine how much silence is needed between segments.
        silence_duration = start_time - self.current_end_time
        self.shape = segment.audio.shape

        # start_time for a TranslatedSentence always matches start_time of the
        # parent Sentence for a video. For podcasts, we don't compress
        # TranslatedSentence so start_time of TranslatedSentence > start_time
        # of orignal Sentence is possible.
        if is_video:
            # Accomodate for floating point errors.
            assert silence_duration > -0.5

        # For podcasts, we cap the max duration of silence.
        if not is_video:
            silence_duration = min(silence_duration, MAX_PODCAST_SILENCE_DURATION)

        silence_frames = silence_duration * self.samplerate
        if silence_frames > 0:
            self.segments.append(
                numpy.zeros((int(silence_frames), segment.audio.shape[1]))
            )
            self.current_end_time += silence_duration

        # Add the new segment
        self.segments.append(segment.audio)
        self.current_end_time += round(
            (segment.audio.shape[0]) / float(self.samplerate), 1
        )

    def stack(self):
        self.audio = numpy.vstack(tuple([i for i in self.segments]))

    # used to ensure uniform shape of final audio
    def add_blank(self, video_length):
        padding = video_length - self.current_end_time
        # this should never happen, due to minimize_speedups code
        assert padding >= 0, "Translation is longer than original video length"

        self.segments.append(
            numpy.zeros((int(padding * self.samplerate), self.shape[1]))
        )


# audio.shape[0] should equal length after this call
def fix_shape(audio, length):
    if audio.shape[0] > length:
        return audio[:length]

    repeats = math.ceil(length / audio.shape[0])
    # else repeat until we hit length
    audio = numpy.concatenate([audio for _ in range(repeats)], axis=0)
    return audio[:length]
