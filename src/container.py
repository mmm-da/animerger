from ffmpeg import probe
import chardet
import pysubs2
import langdetect
import iso639
import enum

from fontTools import ttLib

import settings

# We can convert TTC to TTF files with https://github.com/yhchen/ttc2ttf

class StreamTypes(enum.IntEnum):
    VIDEO = 0
    AUDIO = 1
    SUBTITLE = 2

class MetaContainer:
    def __init__(self, containers_paths, attachments_paths):
        self.__container_list = containers_paths
        self.__stream_list = []
        self.__attach_list = []
        self.__missing_fonts = []

        self.__font_dict = {}
        self.create_font_dict(attachments_paths)

        """Get all stream from containers"""
        for container_id, container_path in enumerate(self.__container_list):
            self.get_streams(container_id, container_path)
            
        self.__stream_list.sort(key=lambda x: x.type)
        self.clean_attachments()

        print("Streams: ")
        for stream in self.__stream_list:
            print(str(stream))
        print("Attachments: ", self.__attach_list)

    @property
    def container_list(self):
        return self.__container_list

    @property
    def stream_list(self):
        return self.__stream_list

    @property
    def attach_list(self):
        return self.__attach_list

    @property
    def missing_fonts(self):
        return self.__missing_fonts

    def create_font_dict(self, attachments_paths: str):
        """ Create dict like {font_name:font_path}

        """
        for attach in attachments_paths:
            self.__font_dict[Font.get_font_name(attach)] = attach

    def clean_attachments(self):
        required_fonts = []
        self.__missing_fonts = []
        for stream in self.__stream_list:
            if stream.type == StreamTypes.SUBTITLE:
                required_fonts += stream.required_fonts        
        for font in required_fonts:
            try:
                self.__attach_list.append(self.__font_dict[font])
            except:
                self.__missing_fonts.append(font)

    def get_streams(self, container_id, container_path):
        """ Create stream entity from all containers.

        """
        stream_path = None
        print("Container №{0} - {1}".format(container_id,container_path))
        ffmpeg_probe = probe(container_path)
        if len(ffmpeg_probe["streams"]) <= 1:
            stream_path = container_path
        for ffmpeg_stream in ffmpeg_probe["streams"]:
            stream_attributes = {}
            if "disposition" in ffmpeg_stream:
                stream_attributes.update(
                    (k, bool(v)) for k, v in ffmpeg_stream["disposition"].items()
                )
            if "tags" in ffmpeg_stream:
                stream_attributes.update(ffmpeg_stream["tags"])
            codec_type = ffmpeg_stream["codec_type"]
            stream_id = ffmpeg_stream["index"]
            if codec_type == "video":
                self.__stream_list.append(
                    VideoStream(container_id, stream_id, stream_attributes)
                )
            elif codec_type == "audio":
                self.__stream_list.append(
                    AudioStream(container_id, stream_id, stream_attributes)
                )
            elif codec_type == "subtitle":
                self.__stream_list.append(
                    SubtitleStream(
                        container_id, stream_id, stream_attributes, stream_path
                    )
                )

class Stream:
    def __init__(
        self, container_id: int, stream_id: int, attributes: dict = {}, path=None
    ):
        self.__container_id = container_id
        self.__stream_id = stream_id
        self.path = path
        self.create_attributes(attributes)

    @property
    def container_id(self):
        return self.__container_id

    @property
    def stream_id(self):
        return self.__stream_id

    def create_attributes(self, attributes: dict):
        default_attr = dict(lang=None, default=None, forced=None)
        allowed_attr = default_attr.keys()
        default_attr.update(attributes)
        self.__dict__.update(
            (k, v) for k, v in default_attr.items() if k in allowed_attr
        )

    def __repr__(self):
        return "{0}:{1} \n({2})\n".format(self.container_id,self.stream_id,self.__dict__)


class VideoStream(Stream):
    def __init__(self, container_id: int, stream_id: int, attributes: dict = {}):
        super().__init__(container_id, stream_id, attributes)
        self.type = StreamTypes.VIDEO


class AudioStream(Stream):
    def __init__(self, container_id: int, stream_id: int, attributes: dict = {}):
        super().__init__(container_id, stream_id, attributes)
        self.type = StreamTypes.AUDIO


class SubtitleStream(Stream):
    """Differs from _Stream_ in a field required_fonts and path"""

    def __init__(
        self, container_id: int, stream_id: int, attributes: dict = {}, path: str = None
    ):
        super().__init__(container_id, stream_id, attributes,path)
        self.type = StreamTypes.SUBTITLE
        
    def create_attributes(self,attributes):
        super().create_attributes(attributes)
        self.__required_fonts = []
        self.__encoding = ""
        """ Update subtitle specific metadata"""
        if self.path != None:
            self.__detect_codepage()
            self.__detect_subtitle_lang()
            self.__detect_required_fonts()

    @property
    def required_fonts(self):
        return self.__required_fonts

    def __detect_subtitle_lang(self):
        if self.path is None:
            return
        subtitle_text = ""
        try:
            subs = pysubs2.load(self.path, encoding=self.__encoding)
            for line in subs:
                subtitle_text += line.text
            lang_alpha2 = langdetect.detect(subtitle_text)
            language = iso639.languages.get(part1=lang_alpha2)
            self.lang = language.part2t
        except UnicodeDecodeError:
            self.lang = ""

    def __detect_codepage(self):
        if self.path is None:
            return
        with open(self.path, "rb") as file:
            self.__encoding = chardet.detect(file.read())["encoding"]

    def __detect_required_fonts(self):
        if self.path is None:
            return
        try:
            subs = pysubs2.load(self.path, encoding=self.__encoding)
            for line in subs:
                try:
                    self.__required_fonts.append(subs.styles[line.style].fontname)
                except KeyError:
                    pass
        except UnicodeDecodeError:
            pass
        self.__required_fonts = list(dict.fromkeys(self.__required_fonts))

class Attach:
    def __init__(self,path):
        self.__path = path


class Font:
    def __init__(self):
        pass

    @staticmethod
    def get_font_name(path):
        font = ttLib.TTFont(path)
        name = ""
        for record in font["name"].names:
            if record.nameID == 4:
                name = str(record)
                break
        return name
