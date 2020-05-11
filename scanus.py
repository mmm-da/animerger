import ass
import re
import os
import pysrt
from iso639 import languages
from langdetect import detect
from pathlib import Path

video_files_extensions = [".mkv", ".mp4", "avi"]
audio_files_extensions = [".mka", ".aac", ".mp3"]
subtitles_files_extensions = [".srt", ".ass", ".ssa"]
attach_font_extensions = [".ttf", ".otf"]


def get_name_templates(path):
    """Scans all files in a folder and subfolders for video files returns a template dict
        
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

    dir = Path(path)
    for child in dir.iterdir():
        if child.is_dir():
            result_dict.update(get_name_templates(child))
        else:
            if child.suffix.lower() in video_files_extensions:
                result_dict[child.stem] = [str(child), [], [], []]
    return result_dict


def detect_subtitle_lang(subtitle_path):
    """Return subtitle language label in ISO 639-2t format

        Keyword arguments:
        subtitle_path -- path to subtitle file
    """
    subtitle_text = ""
    if subtitle_path.suffix == ".ass":
        with open(str(subtitle_path), encoding="utf_8_sig") as file:
            sub = ass.parse(file)
            for i in sub.events:
                subtitle_text += re.sub(r"{.*}", "", i.text)
    elif subtitle_path.suffix == ".srt":
        try:
            sub = pysrt.open(str(subtitle_path))
            pass
        except UnicodeDecodeError:
            sub = pysrt.open(str(subtitle_path), encoding="cp1251")
            pass
        else:
            sub = pysrt.open(str(subtitle_path), encoding="iso-8859-1")
        for i in sub:
            subtitle_text += i.text

    alpha2 = detect(subtitle_text)
    language = languages.get(part1=alpha2)
    return language.part2t


def get_subtitles_from_templates(path, template_dict):
    """Scans all files in a folder and subfolders for subtitles file
        and adds information about subtitles to each template_dict entry
        
        Keyword arguments:
        path -- path to anime release
        template_dict -- template dict from get_name_templates()
        font_dict -- dictionary of fonts located at path

        Subtitle list entity content:
        path -- path to subtitle file
        name -- subtitle label
        lang -- subtitle language label in ISO 639-2t format
        dispose -- mkv subtitle flag
    """

    result_dict = template_dict
    dir = Path(path)
    for child in dir.iterdir():
        if child.is_dir():
            result_dict.update(get_subtitles_from_templates(child, template_dict))
        else:
            if child.suffix.lower() in subtitles_files_extensions:
                parent_dir_name = Path(str(child) + "/..").resolve().stem
                # nested check
                unnested_name = Path(re.sub("." + parent_dir_name, "", child.name)).stem
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


def get_audio_from_templates(path, template_dict):
    """ Scans all files in a folder and subfolders for audio file
        and adds information about audio to each template_dict entry
        
        Keyword arguments:
        path -- path to anime release
        template_dict -- template dict from get_name_templates()

        Audio list entity content:
        path -- path to audio file
        name -- audio label
        lang -- audio language label ISO 639(alpha3)
        dispose -- mkv audio flag
    """

    result_dict = template_dict
    dir = Path(path)
    for child in dir.iterdir():
        if child.is_dir():
            result_dict.update(get_audio_from_templates(child, template_dict))
        else:
            if child.suffix.lower() in audio_files_extensions:
                if child.stem in result_dict:
                    if (Path(str(child) + "/..").resolve().stem) == child.stem:
                        audio_label = ""
                    else:
                        audio_label = Path(str(child) + "/..").resolve().stem
                    audio_entity = [
                        str(child),
                        audio_label,
                        "rus",
                        0,
                    ]
                    result_dict[child.stem][2].append(audio_entity)
    return result_dict


def get_all_font_list(path):
    """Scans all files in a folder and subfolders for font files return list of path to fonts
    
    Keyword arguments:
        path -- path to anime release
    """

    dir = Path(path)
    result_dict = {}
    for child in dir.iterdir():
        if child.is_dir():
            result_dict.update(get_all_font_list(child))
        else:
            if child.suffix.lower() in attach_font_extensions:
                if not (child.name in result_dict):
                    result_dict[child.name] = str(child)
    return result_dict


def scan_directory(path):
    """Scans all files in a folder and subfolders end return dict

        Keyword arguments:
        path -- path to anime release
        
        dict content:
        key -- video file name without extention
        val -- list
                    * absolute path
                    * subtitle list
                    * audio list 
                    * font list
    """
    font_list = list(get_all_font_list(path).values())
    result_dict = get_name_templates(path)
    result_dict = get_subtitles_from_templates(path, result_dict)
    result_dict = get_audio_from_templates(path, result_dict)
    for i in result_dict:
        result_dict[i][3] = font_list
    return result_dict


if __name__ == "__main__":
    print("Scanus isn't executable module")
