import re
import pprint
from pathlib import Path

import chardet
import pysubs2
from iso639 import languages
from langdetect import detect

from file_extentions import (
    audio_extensions,
    fonts_extensions,
    subtitles_extensions,
    video_extensions,
)


class Scanus:
    def __init__(self):
        super().__init__()
        self._search_sp = False
        self._container_dict = {}
        self._font_dict = {}
        
    @property
    def search_sp(self):
        return self._search_sp
    
    @search_sp.setter
    def search_sp(self, value):
        self._search_sp = value

    def _search_templates(self, path):
        # search all video containers
        dir_path = Path(path)
        for child in dir_path.iterdir():
            if child.is_dir():
                if self._search_sp:
                    self._search_templates(child)
            elif child.suffix.lower() in video_extensions:
                self._container_dict[child.stem] = [str(child)]

    def scan_directory(self,dir_path):
        # search all containers
        dir_path = Path(dir_path)
        self._container_dict = {}
        self._font_dict = {}
        
        def _scan_directory(path):
            for child in path.iterdir():
                if child.is_dir():
                    _scan_directory(child)
                elif child.suffix.lower() in (audio_extensions + subtitles_extensions):
                    for template in self._container_dict:
                        template_regex = re.escape(template)
                        if re.match(template_regex,child.name) != None:
                            self._container_dict[template].append(str(child))
                elif child.suffix.lower() in fonts_extensions:
                    self._font_dict[child.name] = str(child)
        
        self._search_templates(dir_path)
        _scan_directory(dir_path)

    def get_container_list(self):
        return list(self._container_dict.values())

    def get_font_list(self):
        return list(self._font_dict.values())

def _get_name_templates(path):
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
            result_dict.update(_get_name_templates(child))
        else:
            if child.suffix.lower() in video_extensions:
                result_dict[child.stem] = [str(child), [], [], []]
    return result_dict


def _detect_codepage(path):
    """Return string with codepage

    Keyword arguments:
    subtitle_path -- path to subtitle file
    """
    with open(path, "rb") as file:
        return chardet.detect(file.read())["encoding"]


def _detect_subtitle_lang(subtitle_path):
    """Return subtitle language label in ISO 639-2t format.

    Keyword arguments:
    subtitle_path -- path to subtitle file
    """
    subtitle_text = ""
    encoding = _detect_codepage(subtitle_path)
    try:
        subs = pysubs2.load(subtitle_path, encoding=encoding)
        for line in subs:
            subtitle_text += line.text
        lang_alpha2 = detect(subtitle_text)
        language = languages.get(part1=lang_alpha2)
        return language.part2t
    except UnicodeDecodeError:
        return ""


def _get_attachments_from_templates(path, template_dict):
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
            result_dict.update(_get_attachments_from_templates(child, template_dict))
        else:
            # audio files section
            if child.suffix.lower() in audio_extensions:
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
            elif child.suffix.lower() in subtitles_extensions:
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
                        _detect_subtitle_lang(child),
                        0,
                    ]
                    result_dict[unnested_name][1].append(subtitle_entity)
    return result_dict


def _get_all_font_list(path):
    """Scans all files in a folder and subfolders for font files return list of path to fonts.
    
    Keyword arguments:
        path -- path to anime release
    """

    path = Path(path)
    result_dict = {}
    for child in path.iterdir():
        if child.is_dir():
            result_dict.update(_get_all_font_list(child))
        else:
            if child.suffix.lower() in fonts_extensions:
                if not (child.name in result_dict):
                    result_dict[child.name] = str(child)
    return result_dict


def scan_directory(path=None):
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
    font_list = list(_get_all_font_list(path).values())
    result_dict = _get_name_templates(path)
    result_dict = _get_attachments_from_templates(path, result_dict)
    for i in result_dict:
        result_dict[i][3] = font_list
    return result_dict


if __name__ == "__main__":
    print("Scanus isn't executable module")