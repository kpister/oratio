import os
from constants.constants import ASSETS_DIR, REPO_PATH
import constants.overlay as overlay_constants
from moviepy.editor import (
    TextClip,
    VideoFileClip,
    ImageClip,
    CompositeVideoClip,
)


def watermark_video_clip(
    dubbed_video, input_lang_code, target_lang_with_durations, include_logo=False
):
    """Adds a logo and language watermark. Doesn't support bechkam videos yet.

	Args:
	dubbed_video: moviepy.VideoFileClip
	include_logo: Boolean. Set to False for sensitive content owned by others.
    target_lang_with_durations: [(str, float)]. First parameter is 
    either the locale or language_code for the dubbed audio. Second parameter is
    the duration of the dubbing. For single-language dubbings, this contains a 
    single element with duration = dubbed_video.duration. For bechkam video, 
    each segment has its own lang_code and duration. Note that this parameter 
    expects that the text overlay start when the dubbed_video starts and ends 
    with it.

	Returns:
	moviepy.VideoFileClip
	"""
    if input_lang_code not in overlay_constants.LANGUAGE_CODE_NAME_MAP:
        print(
            f"{input_lang_code} not in LANGUAGE_CODE_NAME_MAP. Update the map for correct rendering. No watermarking will happen."
        )
        return dubbed_video

    # remove any languages which don't have a lang code mapping
    tmp_target_langs = []
    for lang_code, duration in target_lang_with_durations:
        if lang_code not in overlay_constants.LANGUAGE_CODE_NAME_MAP:
            print(
                f"{lang_code} not in LANGUAGE_CODE_NAME_MAP. Update the map for correct rendering.  No watermarking will happen for {lang_code}."
            )
        else:
            tmp_target_langs.append((lang_code, duration))
    target_lang_with_durations = tmp_target_langs

    video_layers = [dubbed_video]

    dubbed_video_height = dubbed_video.size[1]
    dubbed_video_width = dubbed_video.size[0]

    if include_logo:
        top_right_logo = (
            ImageClip(
                os.path.join(
                    REPO_PATH,
                    ASSETS_DIR,
                    overlay_constants.OPENING_TITLE_IMAGE_FILENAME,
                )
            )
            .set_duration(dubbed_video.duration)
            .resize(height=overlay_constants.LOGO_SIZE_RATIO * dubbed_video_height)
            .margin(right=8, top=8, opacity=0)  # (optional) logo-border
            .set_pos(("right", "top"))
        )
        video_layers.append(top_right_logo)

    languages_text = _get_languages_text(
        input_lang_code,
        target_lang_with_durations,
        dubbed_video_width,
        dubbed_video_height,
    ).set_position((0.7, 0.5), relative=True)

    video_layers.append(languages_text)

    return CompositeVideoClip(video_layers)


def _get_text_clip(input_lang_code, target_lang, duration, frame_width, frame_height):
    text_clip = (
        TextClip(
            f"{overlay_constants.LANGUAGE_CODE_NAME_MAP[target_lang]}",
            color=overlay_constants.LANG_TEXTBOX_FONT_COLOR,
            stroke_color=overlay_constants.LANG_TEXTBOX_FONT_COLOR,
            # Relative position of the text to the textbox.
            align="Center",
            fontsize=overlay_constants.FONT_SIZE_RATIO * frame_width,
            stroke_width=overlay_constants.FONT_STROKE_WIDTH,
            kerning=overlay_constants.FONT_LETTER_SPACING,
            font=overlay_constants.TEXT_FONT,
            size=(
                overlay_constants.LANG_TEXTBOX_WIDTH_RATIO * frame_width,
                overlay_constants.LANG_TEXTBOX_HEIGHT_RATIO * frame_height,
            ),
        )
        .set_duration(duration)
        .set_opacity(overlay_constants.LANG_TEXTBOX_OPACITY)
    )
    return CompositeVideoClip([text_clip])


def _get_languages_text(
    input_lang_code, target_lang_with_durations, frame_width, frame_height
):
    lang_text_clips = [
        _get_text_clip(
            input_lang_code, target_lang, duration, frame_width, frame_height
        )
        for target_lang, duration in target_lang_with_durations
    ]
    return concatenate_videoclips(lang_text_clips)
