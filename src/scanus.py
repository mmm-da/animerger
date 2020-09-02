# -*- coding: utf-8 -*-
"""This module provides a class that scans a folder for any containers
(assuming container is video/audio/subtitle file or font).

Possible file extensions are listed in file_extensions module.
"""
import re
from pathlib import Path

import chardet
import pysubs2
from iso639 import languages
from langdetect import detect

from settings import (
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
        self._attach_dict = {}

    @property
    def search_sp(self):
        return self._search_sp

    @search_sp.setter
    def search_sp(self, value):
        self._search_sp = value

    def _search_templates(self, path):
        """ Search  video containers in path
    
        """
        dir_path = Path(path)
        for child in dir_path.iterdir():
            if child.is_dir():
                if self._search_sp:
                    self._search_templates(child)
            elif child.suffix.lower() in video_extensions:
                self._container_dict[child.stem] = [str(child)]

    def scan_directory(self, dir_path):
        """ Search all containers (video, audio, subtitles, fonts) in dir_path

        """
        dir_path = Path(dir_path)
        self._container_dict = {}
        self._attach_dict = {}

        def _scan_directory(path):
            for child in path.iterdir():
                if child.is_dir():
                    _scan_directory(child)
                elif child.suffix.lower() in (audio_extensions + subtitles_extensions):
                    for template in self._container_dict:
                        template_regex = re.escape(template)
                        if re.match(template_regex, child.name) != None:
                            self._container_dict[template].append(str(child))
                elif child.suffix.lower() in fonts_extensions:
                    self._attach_dict[child.name] = str(child)

        self._search_templates(dir_path)
        _scan_directory(dir_path)

    @property
    def container_list(self):
        return list(self._container_dict.values())

    @property
    def attach_list(self):
        return list(self._attach_dict.values())


if __name__ == "__main__":
    print("Scanus isn't executable module")
