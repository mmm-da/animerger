import pathlib
import anitopy
from ffmpeg import probe
import chardet
import pysubs2
import langdetect
import iso639
import enum

import settings



class StreamTypes(enum.IntEnum):
    VIDEO = 0
    AUDIO = 1
    SUBTITLE = 2


class MetaContainer:
    def __init__(
        self,
        containers_paths,
        attachments_paths,
        name_template: str = None,
        title=None,
        parse_name: bool = False,
    ):
        self.__container_list = containers_paths
        self.__stream_list = []
        self.__attach_list = []
        self.__missing_fonts = []

        self.__create_attach_list(attachments_paths)
        if parse_name:
            name_info = self.__parse_name(self.container_list[0])
            if name_info:
                if title:
                    name_info["title"] = title
                if name_info["ep_num"] is None:
                    name_info["ep_num"] = ""
                if name_template:
                    # TEMPLATE UNIMPLEMENTED MAGIC
                    pass
                else:
                    # Default template is "Title EpNum.mkv"
                    self.__name = "{0} {1}.mkv".format(
                        name_info["title"], name_info["ep_num"]
                    )
            else:
                self.__name = pathlib.Path(self.container_list[0]).name
        else:
            self.__name = pathlib.Path(self.container_list[0]).name

        """Get all stream from containers"""
        for container_id, container_path in enumerate(self.__container_list):
            self.__get_streams(container_id, container_path)

        self.__stream_list.sort(key=lambda x: x.type)

    @property
    def name(self):
        return self.__name

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

    def __parse_name(self, name: str) -> dict:
        anitopy_options = dict(
            {
                "parse_episode_number": True,
                "parse_episode_title": False,
                "parse_file_extension": False,
                "parse_release_group": False,
            }
        )
        parse_result = anitopy.parse(name, options=anitopy_options)
        if (parse_result["anime_title"] is not None) and (
            parse_result["episode_number"] is not None
        ):
            parse_result["anime_title"] = pathlib.Path(parse_result["anime_title"]).name
            return dict(
                {
                    "title": parse_result["anime_title"],
                    "ep_num": parse_result["episode_number"],
                }
            )
        else:
            return None

    def __create_font_dict(self, attachments_paths: str):
        """Create dict like {font_name:font_path}"""
        for attach in attachments_paths:
            self.__attach_list.append(attach)

    def __get_streams(self, container_id, container_path):
        """Create stream entity from all containers."""
        stream_path = None
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
        return "{0}:{1} \n({2})\n".format(
            self.container_id, self.stream_id, self.__dict__
        )


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
        super().__init__(container_id, stream_id, attributes, path)
        self.type = StreamTypes.SUBTITLE

    def create_attributes(self, attributes):
        super().create_attributes(attributes)
        self.__required_fonts = []
        self.__encoding = ""
        """ Update subtitle specific metadata"""
        if self.path != None:
            self.__detect_codepage()
            self.__detect_subtitle_lang()

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


class Attach:
    def __init__(self, path):
        self.__path = path