"""
Usage:
    main.py [<config.yaml>]
"""

import os
import sys
import yaml

from config import Config
from project import Project
from video_project import VideoProject
from constants.constants import SentenceIoMode, REPO_PATH


"""Run parameters"""
config_file = os.path.join(REPO_PATH, "config.yaml")

if len(sys.argv) > 2:
    raise RuntimeError("Invalid arguments")

# override the default config file
if len(sys.argv) == 2:
    config_file = sys.argv[1]

if not os.path.isfile(config_file):
    raise FileNotFoundError("Config file does not exist")

with open(config_file) as f:
    config = Config(yaml.load(f.read()))

if config.is_video:
    project = VideoProject(config)
else:
    project = Project(config)


if config.use_config_workflow:
    upload_flac_to_cloud_bucket = config.upload_to_cloud
    need_to_transcribe = config.transcribe
    need_to_translate = config.translate
    need_to_synthesize = config.synthesize
    save_dubbed_videos = config.save_to_disk
else:
    upload_flac_to_cloud_bucket = input("Is file upload needed? (y/N) ") == "y"
    need_to_transcribe = (
        input(
            "Is transcription needed? (y/N). [WARNING] this will overwrite existing transcription. "
        )
        == "y"
    )


if upload_flac_to_cloud_bucket:
    project.upload_flac_to_cloud_bucket()

if need_to_transcribe:
    project.transcribe_sentences()
    project.save_sentences(SentenceIoMode.TRANSCRIBE)
    input("\aPress <enter> to continue (will reload sentences from disk)")

project.load_sentences(SentenceIoMode.TRANSCRIBE)

if not config.use_config_workflow:
    need_to_translate = (
        input(
            "Is translation needed? (y/N). [WARNING] this will overwrite existing translation. "
        )
        == "y"
    )
if need_to_translate:
    project.translate_sentences()
    project.save_sentences(SentenceIoMode.TRANSLATE)
    input("\aPress <enter> to continue (will reload sentences from disk)")

project.load_sentences(SentenceIoMode.TRANSLATE)

if not config.use_config_workflow:
    need_to_synthesize = (
        input(
            "Is synthesis needed? (y/N). [WARNING] this will overwrite existing dubbed audio files. "
        )
        == "y"
    )
if need_to_synthesize:
    project.synthesize_voices()
    project.process_translated_audio()
    project.save_audio_sentences()
    print("\a")
else:
    project.load_audio_sentences()

if config.use_original_bg:
    project.create_original_audio_mask()
project.generate_tracks()
if config.match_original_voice_volume:
    project.create_original_volume_mask()
project.save_tracks()

if type(project) == VideoProject:
    if not config.use_config_workflow:
        save_dubbed_videos = (
            input("Do you want to save these videos to disk? (y/N) ") == "y"
        )
    if save_dubbed_videos:
        project.overlay_dubbing_and_save()
        print("\a")
