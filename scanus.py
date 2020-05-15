import ass
import re
import pysrt
from iso639 import languages
from langdetect import detect
from pathlib import Path

video_files_extensions = [".mkv", ".mp4", ".avi"]
audio_files_extensions = [".mka", ".aac", ".mp3", ".ac3"]
subtitles_files_extensions = [".srt", ".ass", ".ssa"]
attach_font_extensions = [".ttf", ".otf"]


def get_name_templates(path):
    """Scans all files in a folder and subfolders for video files returns a template dict.
        
    Keyword arguments:
    path -- path to anime release

    template dict content:
    key -- video file name without extention
    val -- list
                * absolute path
                * empty subtitle list
                * empty audio list
                * empty font list
    """

    result_dict = {}

    path = Path(path)
    for child in path.iterdir():
        if child.is_dir():
            result_dict.update(get_name_templates(child))
        else:
            if child.suffix.lower() in video_files_extensions:
                result_dict[child.stem] = [str(child), [], [], []]
    return result_dict


def detect_subtitle_lang(subtitle_path):
    """Return subtitle language label in ISO 639-2t format.

    Keyword arguments:
    subtitle_path -- path to subtitle file
    """
    subtitle_text = ""
    if subtitle_path.suffix in [".ass", ".ssa"]:
        with open(str(subtitle_path), encoding="utf_8_sig") as file:
            sub = ass.parse(file)
            for i in sub.events:
                subtitle_text += re.sub(r"{.*}", "", i.text)
    elif subtitle_path.suffix == ".srt":
        try:
            sub = pysrt.open(str(subtitle_path))
        except UnicodeDecodeError:
            sub = pysrt.open(str(subtitle_path), encoding="cp1251")
        else:
            # detect not possible
            return ""
        for i in sub:
            subtitle_text += i.text
    else:
        # detect not possible
        return ""
    alpha2 = detect(subtitle_text)
    language = languages.get(part1=alpha2)
    return language.part2t


def get_attachments_from_templates(path, template_dict):
    """ Scans all files in a folder and subfolders for audio or subtitle file and adds information about it to each template_dict entry.
        
    Keyword arguments:
    path -- path to anime release
    template_dict -- template dict from get_name_templates()

    Audio list entity content:
    path -- path to audio file
    name -- audio label
    lang -- audio language label ISO 639-2t format
    dispose -- mkv audio flag

    Subtitle list entity content:
    path -- path to subtitle file
    name -- subtitle label
    lang -- subtitle language label in ISO 639-2t format
    dispose -- mkv subtitle flag
    """

    result_dict = template_dict
    path = Path(path)
    for child in path.iterdir():
        if child.is_dir():
            result_dict.update(get_attachments_from_templates(child, template_dict))
        else:
            # audio files section
            if child.suffix.lower() in audio_files_extensions:
                if child.stem in result_dict:
                    if (Path(str(child) + "/..").resolve().stem) == child.stem:
                        audio_label = ""
                    else:
                        audio_label = Path(str(child) + "/..").resolve().stem
                    audio_entity = [
                        str(child),
                        audio_label,
                        "",
                        0,
                    ]
                    result_dict[child.stem][2].append(audio_entity)
            # subtitle files section
            elif child.suffix.lower() in subtitles_files_extensions:
                parent_dir_name = Path(str(child) + "/..").resolve().stem
                # nested check
                unnested_name = Path(
                    re.sub(r"\." + re.escape(parent_dir_name), "", child.name)
                ).stem
                if unnested_name in result_dict:
                    subtitle_label = parent_dir_name
                    subtitle_entity = [
                        str(child),
                        subtitle_label,
                        detect_subtitle_lang(child),
                        0,
                    ]
                    result_dict[unnested_name][1].append(subtitle_entity)
    return result_dict


def get_all_font_list(path):
    """Scans all files in a folder and subfolders for font files return list of path to fonts.
    
    Keyword arguments:
        path -- path to anime release
    """

    path = Path(path)
    result_dict = {}
    for child in path.iterdir():
        if child.is_dir():
            result_dict.update(get_all_font_list(child))
        else:
            if child.suffix.lower() in attach_font_extensions:
                if not (child.name in result_dict):
                    result_dict[child.name] = str(child)
    return result_dict


def scan_directory(path = None):
    """Scans all files in a folder and subfolders end return dict.

    Keyword arguments:
    path -- path to anime release. Uses current directory by default

    dict content:
    key -- video file name without extention
    val -- list
        * absolute path
        * subtitle list
        * audio list
        * font list
    """
    if path is None:
        path = Path.cwd()
    font_list = list(get_all_font_list(path).values())
    result_dict = get_name_templates(path)
    result_dict = get_attachments_from_templates(path, result_dict)
    for i in result_dict:
        result_dict[i][3] = font_list
    return result_dict


if __name__ == "__main__":
    print("Scanus isn't executable module")
