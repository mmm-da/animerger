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

if __name__ == "__main__":
    print("Scanus isn't executable module")
