import os
import subprocess
from iso639 import languages
from ffmpeg import probe


class Container:

    def __init__(self):
        super().__init__()
        self.audio = []
        self.video = []
        self.subtitles = []
        self.fonts = []
        self.containers = []
        self.name = None

    def add_stream(self, stream_type, path, name=None, lang=None, disposition=None):
        if stream_type == "font":
            self.fonts.append(path)
            return

        if lang is None or lang == '':
            lang = "und"
        else:
            name = languages.get(part2t=lang).name

        if name is None or name == '':
            if lang is None:
                name = "Undefined language"
            else:
                name = languages.get(part2t=lang).name + " language"

        stream = {"name": name, "language": lang, "path": path}

        if disposition is not None:
            stream["disposition"] = disposition
        else:
            stream["disposition"] = {
                "attached_pic": 0,
                "clean_effects": 0,
                "comment": 0,
                "default": 0,
                "dub": 0,
                "forced": 0,
                "hearing_impaired": 0,
                "karaoke": 0,
                "lyrics": 0,
                "original": 0,
                "timed_thumbnails": 0,
                "visual_impaired": 0,
            }
        if stream_type == "audio":
            self.audio.append(stream)
        elif stream_type == "video":
            self.video.append(stream)
        elif stream_type == "subtitles":
            self.subtitles.append(stream)

    def add_container(self, path):
        container = probe(path)
        for stream in container["streams"]:
            stream_properties = {}
            if "tags" in stream:
                tags = stream["tags"]
                for field in tags:
                    stream_properties[field] = tags[field]
            if "language" not in stream_properties:
                stream_properties["language"] = "und"
            if "name" not in stream_properties:
                stream_properties["name"] = languages.get(part2t=stream_properties["language"]).name + " language"
            stream_properties["disposition"] = stream["disposition"]
            stream_properties["path"] = "container"
            if stream["codec_type"] == "audio":
                self.audio.append(stream_properties)
            elif stream["codec_type"] == "video":
                self.video.append(stream_properties)
            elif stream["codec_type"] == "subtitle":
                self.subtitles.append(stream_properties)
        self.containers.append(path)

    def add_name(self, name):
        self.name = name

    def compile(self):
        # Order of streams:
        # 1. Video
        # 2. Audio
        # 3. Subtitles
        # 4. Fonts

        if self.name is None:
            return "Can't pack container without name"

        cmd = "ffmpeg"
        current_stream = 0

        containers_nb = 0
        # We should attach all containers
        for cont in self.containers:
            cmd += ' -i "{}"'.format(cont)
            containers_nb += 1
        for stream in self.video:
            if stream["path"] != 'container':
                cmd += ' -i "{}"'.format(stream["path"])
                containers_nb += 1
        for stream in self.audio:
            if stream["path"] != 'container':
                cmd += ' -i "{}"'.format(stream["path"])
                containers_nb += 1
        for stream in self.subtitles:
            if stream["path"] != 'container':
                cmd += ' -i "{}"'.format(stream["path"])
                containers_nb += 1

        for stream in self.video:
            # TODO: Handle disposition field
            # TODO: don't assume anything about stream number
            cmd += " -metadata:s:{} language={}".format(current_stream, stream["language"])
            current_stream += 1
        
        for stream in self.audio:
            # TODO: Handle disposition field
            # TODO: don't assume anything about stream number
            cmd += " -metadata:s:{} language={}".format(current_stream, stream["language"])
            current_stream += 1

        for stream in self.subtitles:
            # TODO: Handle disposition field
            # TODO: don't assume anything about stream number
            cmd += " -metadata:s:{} language={}".format(current_stream, stream["language"])
            current_stream += 1
        
        for font in self.fonts:
            cmd += ' -attach "{}" -metadata:s:{} mimetype=application/x-truetype-font'.format(font, current_stream)
            current_stream += 1
        
        # Don't touch audio/video codec
        cmd += " -c:v copy -c:a copy"

        # Map ALL inputs to output
        for input_file in range(containers_nb):
            cmd += " -map {}".format(input_file)

        cmd += ' "{}.mkv"'.format(self.name)

        return cmd

    def show_streams(self):
        from pprint import pprint
        pprint(self.audio)
        pprint(self.video)
        pprint(self.subtitles)
        pprint(self.fonts)

