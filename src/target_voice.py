from google.cloud.texttospeech import SsmlVoiceGender


class TargetVoice:
    def __init__(
        self,
        lang_code,
        locale,
        gcloud_ssml_voice_gender,
        gcloud_voicename=None,
        aws_voice_id=None,
    ):
        # ISO 639-1 identifier for gCloud translate API.
        self.lang_code = lang_code
        # Locales for gCloud TTS API.
        self.locale = locale
        self.gender = gcloud_ssml_voice_gender
        self.gcloud_name = gcloud_voicename
        self.aws_voice_id = aws_voice_id

        if aws_voice_id is not None:
            self.name = aws_voice_id
        if gcloud_voicename is not None:
            self.name = gcloud_voicename

    def __str__(self):
        if self.aws_voice_id:
            return f"Using AWS Voice: {self.aws_voice_id} \
                      Locale: {self.locale} \
                      Gender: {gender_string(self.gender)}"
        if self.gcloud_name:
            return f"Using GCloud Voice: {self.gcloud_name} \
                      Locale: {self.locale} \
                      Gender: {gender_string(self.gender)}"


def gender_string(gender):
    if gender in ["male", "female", "unknown"]:
        return gender  # already a string
    if gender == SsmlVoiceGender.MALE:
        return "male"
    if gender == SsmlVoiceGender.FEMALE:
        return "female"
    if int(gender) == 1:
        return "male"
    if int(gender) == 2:
        return "female"
    return "unknown"


def gender_number(gender):
    if gender == SsmlVoiceGender.MALE:
        return 1
    if gender == SsmlVoiceGender.FEMALE:
        return 2
    if int(gender) == "male":
        return 1
    if int(gender) == "female":
        return 2
    return 3


def convert_gender(gender_string):
    if gender_string in [1, 2]:
        return gender_string  # it wasn't actually a string...

    assert gender_string.lower() in ["male", "female"]

    if gender_string.lower() == "male":
        return SsmlVoiceGender.MALE
    elif gender_string.lower() == "female":
        return SsmlVoiceGender.FEMALE


def get_lang_code(locale):
    if locale.startswith("cmn"):
        return "zh"
    elif locale.startswith("fil"):
        return "tl"
    elif locale.startswith("nb"):
        return "no"
    elif "-" in locale:
        return locale.split("-")[0]
    return locale


def create_voice(locale, gender, gcloud_name=None, voiceId=None):
    # assert locale in provider_locales # TODO
    assert "-" in locale
    lang_code = get_lang_code(locale)
    gender = convert_gender(gender)

    return TargetVoice(
        lang_code, locale, gender, gcloud_voicename=gcloud_name, aws_voice_id=voiceId
    )
