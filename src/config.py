from google.cloud.texttospeech import SsmlVoiceGender

from constants.constants import *
from constants.overlay import *

from client import Provider, Client
from target_voice import get_lang_code


class Config:
    def __init__(self, args):
        self.args = args
        # required params
        self.project_name = self.get(
            "project_name", required=True, validate=validate_project_name
        )
        self.input_locale = self.get(
            "input_locale", required=True, validate=validate_locale
        )
        self.input_media_file = self.get(
            "input_media_file", required=True, validate=validate_file
        )
        self.target_locales = self.get(
            "target_locales", required=True, validate=validate_locales
        )
        self.gender = self.get("gender", required=True, vtype=SsmlVoiceGender)

        # video flags
        if self.is_video():
            self.beckham = self.get("beckham", vtype=bool)
            if self.beckham:
                self.beckham_rotation_speed = self.get(
                    "beckham_rotation_speed", vtype=int, default=1
                )
            self.include_watermarks = self.get("include_watermarks", vtype=bool)
            self.export_fps = self.get(
                "export_fps", vtype=int, default=0, validate=validate_fps
            )
            self.gcloud_speedup = self.get("gcloud_speedup", vtype=bool)

        # provider flags
        self.stt_provider = self.get(
            "stt_provider", vtype=Provider, default=Provider.GCLOUD
        )
        self.translate_provider = self.get(
            "translate_provider", vtype=Provider, default=Provider.GCLOUD
        )
        self.tts_provider = self.get(
            "tts_provider", vtype=Provider, default=Provider.GCLOUD
        )
        # create the client from the providers and gender
        self.client = Client(
            upload_filename=self.project_name
            + "_"
            + (DEFAULT_STT_INPUT_FILENAME + DEFAULT_STT_INPUT_FORMAT),
            stt_provider=self.stt_provider,
            translate_provider=self.translate_provider,
            tts_provider=self.tts_provider,
            gcloud_speedup=self.gcloud_speedup,
            gender=self.gender,
        )

        # decoration
        self.match_original_voice_volume = self.get(
            "match_original_voice_volume", vtype=bool
        )
        self.use_original_bg = self.get("use_original_bg", vtype=bool)

        self.use_background_music = self.get("use_background_music", vtype=bool)
        if self.use_background_music:
            self.background_music_file = self.get(
                "background_music_file",
                default="default_background.wav",
                validate=validate_music_file,
            )

        self.use_best_voices = self.get("use_best_voices", vtype=bool)
        if self.use_best_voices:
            self.best_voices_file = self.get(
                "best_voices_file",
                default="best_voices.json",
                validate=validate_best_voices_file,
            )

        self.production_dir = self.get("production_dir", default="media/prod")
        self.development_dir = self.get("development_dir", default="media/dev")
        self.prod_path = os.path.join(REPO_PATH, self.production_dir, self.project_name)
        self.dev_path = os.path.join(REPO_PATH, self.development_dir, self.project_name)

        # workflow speedup, used in main to jump workflow steps
        self.use_config_workflow = self.get("use_config_workflow", vtype=bool)
        self.upload_to_cloud = self.get("upload_to_cloud", vtype=bool)
        self.transcribe = self.get("transcribe", vtype=bool)
        self.translate = self.get("translate", vtype=bool)
        self.synthesize = self.get("synthesize", vtype=bool)
        self.save_to_disk = self.get("save_to_disk", vtype=bool)

        self.validate_args()

    # How we retrieve and validate our configuration
    def get(self, param, required=False, vtype=None, default=None, validate=None):
        """ 
            param: the value to grab from the dictionary
            required: if set to true, the return must be non-None
            vtype: the type of the value, bool, str, int
            default: if the value is None, set to default
            validate: a function to run on value
        """
        val = self.args.get(param)  # returns None if param not in args

        if val is None:
            if default is not None:
                print(f"{param} not set. Using default: {default}")
            val = default

        # cast the val to be vtype
        if vtype is not None:
            val = vtype(val)

        if required and val is None:
            raise ValueError(f"{param} did not receive a value as input")

        if validate is not None:
            validate(val)

        return val

    def is_video(self):
        return os.path.splitext(self.input_media_file)[1] in VIDEO_FILE_EXTENSIONS

    def validate_args(self):
        if not self.is_video():
            # beckham on videos only [warning]
            if self.beckham:
                print("[Warning] Beckham flag set on non video")
            # watermarks on videos only [warning]
            if self.include_watermarks:
                print("[Warning] Include watermarks flag set on non video")
            # export_fps on videos only [warning]
            if self.export_fps:
                print("[Warning] Export fps flag set on non video")

        # self.production_path exists
        if not os.path.isdir(self.prod_path):
            raise FileNotFoundError(f"Production path {self.prod_path} does not exist")

        # self.development_path exists [create if it doesn't]
        if not os.path.isdir(self.dev_path):
            os.makedirs(self.dev_path)

        # if we want all available langs, get those now
        # availability depends on tts provider (gender must match)
        if self.target_locales == ["all"]:
            voices = self.client.get_all_matching_voices()
            self.target_locales = list(set([v.locale for v in voices]))

        self.target_locales = sorted(self.target_locales)
        self.target_languages = list(set(map(get_lang_code, self.target_locales)))
        self.input_language = get_lang_code(self.input_locale)

        # create beckham directories
        if self.beckham:
            if not os.path.isdir(os.path.join(self.dev_path, "beckham")):
                os.mkdir(os.path.join(self.dev_path, "beckham"))
            if not os.path.isdir(os.path.join(self.prod_path, "beckham")):
                os.mkdir(os.path.join(self.prod_path, "beckham"))

        # all target_locales should be directories in dev to store tmp files
        for locale in self.target_locales + [self.input_locale]:
            # mkdirs in /dev
            if not os.path.isdir(os.path.join(self.dev_path, locale)):
                os.mkdir(os.path.join(self.dev_path, locale))

            # mkdirs in /prod if we are not a beckham video
            if not self.beckham and not os.path.isdir(
                os.path.join(self.prod_path, locale)
            ):
                os.mkdir(os.path.join(self.prod_path, locale))

        # remove the input_locale from targets so we don't translate/synthesize
        if self.input_locale in self.target_locales:
            self.target_locales.remove(self.input_locale)
            self.target_languages.remove(self.input_language)

        # input_media_file exists
        self.input_media_path = os.path.join(self.prod_path, self.input_media_file)
        if not os.path.isfile(self.input_media_path):
            raise FileNotFoundError(
                f"Media file {self.input_media_path} does not exist"
            )

        # set best_voices_path
        if self.use_best_voices:
            self.best_voices_path = os.path.join(REPO_PATH, self.best_voices_file)
            if not os.path.isfile(self.best_voices_path):
                raise FileNotFoundError(
                    f"Best voices file {self.best_voices_path} does not exist"
                )

        # set background_music_path
        if self.use_background_music:
            self.background_music_path = os.path.join(
                REPO_PATH, MUSIC_DIRECTORY, self.background_music_file
            )
            if not os.path.isfile(self.background_music_path):
                raise FileNotFoundError(
                    f"Background music file {self.background_music_path} does not exist"
                )

        if self.use_background_music and self.use_original_bg:
            raise ValueError("Cannot use background music and original background")

        return 0


# VALIDATORS

# This section contains custom validators for config arguments
def validate_project_name(name):
    # project name should be non empty
    if name == "":
        raise ValueError("Project name must be non-empty")


def validate_locale(locale):
    if locale == "all":
        return

    # locale must contain "-" (from observation)
    if "-" not in locale:
        raise ValueError(f"Locale '{locale}' does not contain '-'")

    # locale must exist in our list of locales


def validate_locales(locale_list):
    for locale in locale_list:
        validate_locale(locale)


def validate_file(filename):
    # file must have an extension
    if "." not in filename:
        raise ValueError(f"File {filename} must have a valid extension")


def validate_watermarks(b):
    validate_is_video(b)
    # input locale must be in dictionary
    if b and self.input_locale not in LANGUAGE_CODE_NAME_MAP:
        raise ValueError(f"Locale {self.input_locale} not in LANGUAGE_CODE_NAME_MAP")

    # output locales must be in dictionary
    for out_locale in self.out_locales:
        if b and out_locale not in LANGUAGE_CODE_NAME_MAP:
            raise ValueError(f"Locale {out_locale} not in LANGUAGE_CODE_NAME_MAP")


def validate_music_file(filename):
    if os.path.splitext(filename)[1] != ".wav":
        raise ValueError("Music file type is incompatible. Must be .wav")


def validate_best_voices_file(filename):
    if os.path.splitext(filename)[1] != ".json":
        raise ValueError("Best voices file type is incompatible. Must be .json")


def validate_fps(fps):
    if fps < 0:
        raise ValueError("Cannot have negative FPS")
    if fps > 120:
        raise ValueError("FPS cost is too expensive")
