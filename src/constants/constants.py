import os
import enum

VIDEO_FILE_EXTENSIONS = [".mp4", ".mov"]

DEFAULT_AUDIO_OUTPUT_FORMAT = ".wav"
DEFAULT_VIDEO_OUTPUT_FORMAT = ".mov"
DEFAULT_STT_INPUT_FORMAT = ".flac"
DEFAULT_STT_INPUT_FILENAME = "original_audio"
TRANSCRIBED_SENTENCES_FILENAME = "transcribed_sentences.json"
TRANSLATED_SENTENCES_FILENAME = "translated_sentences.json"

MAX_PODCAST_SILENCE_DURATION = 1.5  # Seconds
BACKGROUND_MUSIC_INTENSITY = 0.50

ORIGINAL_VIDEO_FILENAME = "original_video"
DUBBED_AUDIO_FILENAME = "full_dubbed" + DEFAULT_AUDIO_OUTPUT_FORMAT
DUBBED_COMPOSITE_FILENAME = "dubbed_video" + DEFAULT_VIDEO_OUTPUT_FORMAT
DEFAULT_CODEC_FOR_DUBBED_VIDEO = "libx264"
# Used for saving files
def build_repo_path():
    path = os.getcwd().split("/")
    assert REPO_NAME in path
    ret = []
    for folder in path:
        ret.append(folder)
        if folder == REPO_NAME:
            break
    return "/".join(ret)


REPO_NAME = "oratio"
REPO_PATH = build_repo_path()
TEST_DIR = os.path.join(REPO_PATH, "media/test")
MEDIA_DIRECTORY = "media"
PROD_DIRECTORY = "prod"
DEV_DIRECTORY = "dev"
MUSIC_DIRECTORY = "media/music"
MEDIA_PROD_PATH = os.path.join(MEDIA_DIRECTORY, PROD_DIRECTORY)
MEDIA_DEV_PATH = os.path.join(MEDIA_DIRECTORY, DEV_DIRECTORY)
ASSETS_DIR = os.path.join(MEDIA_DIRECTORY, "assets")
AWS_REGION = "us-east-2.amazonaws.com"
AWS_UPLOAD_BUCKET_NAME = ""  # TODO Must be filled in
AWS_UPLOAD_BUCKET_URL = f"https://{AWS_UPLOAD_BUCKET_NAME}.s3.{AWS_REGION}.com"
GCLOUD_UPLOAD_BUCKET_NAME = ""  # TODO Must be filled in
GCLOUD_UPLOAD_BUCKET_URL = "gs://" + GCLOUD_UPLOAD_BUCKET_NAME

EOS_PUNCTUATION = [".", "?", "!"]


# creating enumerations using class
class SentenceIoMode(enum.Enum):
    UNSPECIFIED_SENTENCE_IO_MODE = 0
    TRANSCRIBE = 1
    TRANSLATE = 2
    # SYNTHESIZE = 3
