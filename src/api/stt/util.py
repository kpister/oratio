# Util.py
from sentence import Sentence
import os
import time
import math

from constants.constants import EOS_PUNCTUATION


class Word:
    def __init__(self, text, start_time, end_time, is_punc=False):
        self.text = text
        self.start = start_time
        self.end = end_time
        self.is_punc = is_punc


def _has_punctuation(word):
    return any([(punctuation in word) for punctuation in EOS_PUNCTUATION])


def create_sentences_from_word_list(results, locale):
    # results :: [words]
    # words :: {
    #   start :: float
    #   end :: float
    #   text :: string
    #   is_punch :: bool
    # }
    sentences = []

    sentence = ""
    sentence_start = 0
    for word in results:
        if sentence_start == 0:
            sentence_start = word.start

        sentence += word.text
        if word.is_punc and word.text in EOS_PUNCTUATION:
            sentence_end = word.end
            # noticeably, speaker and gender are not passed as params... they are added
            # to each sentence instance after this during project.diarize_sentences()
            sentences.append(Sentence(sentence_start, sentence_end, locale, sentence))
            # Reset the counter.
            sentence = ""
            sentence_start = 0
        else:
            sentence += " "

    # Not all transcripts in best_alternative end with a full-stop. In other
    # words, it is not necessary that each that the last word in
    # best_alternative.wordswill have a fullstop.
    if sentence:
        sentence_end = word.end
        sentences.append(Sentence(sentence_start, sentence_end, locale, sentence))

    return sentences
