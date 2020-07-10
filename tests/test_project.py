import test_sentence
import __init__

from project import Project
from sentence import Sentence
from config import Config


def create_mock_project(config):
    sentences = [
        test_sentence.create_mock_sentence(start=0, duration=10),
        test_sentence.create_mock_sentence(start=10, duration=5),
        test_sentence.create_mock_sentence(start=20, duration=20),
    ]

    af = "test_dub.wav"
    test_sentence.create_mock_translation(sentences[0], af, "es-ES")
    test_sentence.create_mock_translation(sentences[1], af, "es-ES")
    test_sentence.create_mock_translation(sentences[2], af, "es-ES")

    af = "test_byte_array"
    test_sentence.create_mock_translation(sentences[0], af, "fr-FR")
    test_sentence.create_mock_translation(sentences[1], af, "fr-FR")
    test_sentence.create_mock_translation(sentences[2], af, "fr-FR")

    prj = Project(config)
    prj.sentences = sentences
    prj.process_translated_audio()
    return prj


def main():
    args = {
        "project_name": "TestProject",
        "input_media_file": "test.mp4",
        "input_locale": "es-ES",
        "gender": 1,
        "target_locales": ["es-ES", "fr-FR"],
        "production_dir": "media/test",
        "development_dir": "media/test",
    }
    config = Config(args)

    print("Testing project creating and saving")
    prj = create_mock_project(config)
    # Test save_to_disk
    prj.generate_tracks()
    prj.save_tracks()
    print("Project saved successfully")

    # Test overlay_dubbing_and_save
    # TODO

    return 0


if __name__ == "__main__":
    main()
