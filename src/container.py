from ffmpeg import probe
import chardet
import pysubs2
import langdetect
import iso639
from fontTools import ttLib

import settings

# We can convert TTC to TTF files with https://github.com/yhchen/ttc2ttf


class FFMpegConf:
    def __init__(self):
        pass


class Container:
    def __init__(self, path: str = None, attachments=[]):
        if path is None:
            return
        self.__stream_list = []
        ffmpeg_probe = probe(path)
        for ffmpeg_stream in ffmpeg_probe['streams']:
            stream_attributes = {}
            if 'disposition' in ffmpeg_stream:
                stream_attributes.update((k, bool(v)) for k, v in ffmpeg_stream['disposition'].items())
            if 'tags' in ffmpeg_stream:
                stream_attributes.update(ffmpeg_stream['tags'])
            codec_type = ffmpeg_stream['codec_type']
            stream_id = ffmpeg_stream['index']
            if codec_type == 'video':
                stream_instance = VideoStream(stream_id, stream_attributes)
            elif codec_type == 'audio':
                stream_instance = VideoStream(stream_id, stream_attributes)
            elif codec_type == 'subtitle':
                # Pass subtitle file path only if they aren't embedded
                if path.rpartition('.')[-1] in settings.subtitles_extensions:
                    subtitle_path = path
                else:
                    subtitle_path = None
                stream_instance = SubtitleStream(stream_id, subtitle_path, stream_attributes)
            else:
                stream_instance = Stream(stream_id, stream_attributes)
            self.__stream_list.append(stream_instance)
        self.__attach_list = []

    def compile_cmd(self, compiler=None, compiler_config=None) -> str:
        return ""

    def join(self, other):
        new_container = Container()
        new_container.__stream_list = self.__stream_list.extend(other.__stream_list)
        new_container.__attach_list = self.__attach_list.extend(other.__attach_list)
        return new_container


class Stream:
    """This class represents a Stream, which is a _media_ file (not a font or something)"""

    def __init__(self, stream_id: int, attributes: dict = {}):
        self.__stream_id = stream_id
        # Set attributes of stream
        default_attr = dict(lang=None, default=None, forced=None)
        allowed_attr = default_attr.keys()
        default_attr.update(attributes)
        self.__dict__.update((k, v) for k, v in default_attr.items() if k in allowed_attr)

    @property
    def stream_id(self):
        return self.__stream_id


class SubtitleStream(Stream):
    """Differs from _Stream_ in a field required_fonts and path"""

    def __init__(self, stream_id: int, path: str = None, attributes: dict = {}):
        super().__init__(stream_id, attributes)
        self.__path = path
        self.__required_fonts = []
        self.__encoding = ""
        """ Update subtitle specific metadata"""
        self.__detect_codepage()
        self.__detect_subtitle_lang()
        self.__detect_required_fonts()

    @property
    def required_fonts(self):
        return self.__required_fonts

    def __detect_subtitle_lang(self):
        if self.__path is None:
            return
        subtitle_text = ""
        try:
            subs = pysubs2.load(self.__path, encoding=self.__encoding)
            for line in subs:
                subtitle_text += line.text
            lang_alpha2 = langdetect.detect(subtitle_text)
            language = iso639.languages.get(part1=lang_alpha2)
            self.lang = language.part2t
        except UnicodeDecodeError:
            self.lang = ""

    def __detect_codepage(self):
        if self.__path is None:
            return
        with open(self.__path, "rb") as file:
            self.__encoding = chardet.detect(file.read())["encoding"]
    
    def __detect_required_fonts(self):
        if self.__path is None:
            return
        try:
            subs = pysubs2.load(self.__path, encoding=self.__encoding)
            for line in subs:
                self.__required_fonts.append(subs.styles[line.style].fontname)
        except UnicodeDecodeError:
            pass
        self.__required_fonts = list(dict.fromkeys(self.__required_fonts))


class VideoStream(Stream):

    def __init__(self, stream_id: int, attributes: dict = {}):
        super().__init__(stream_id, attributes)


class AudioStream(Stream):

    def __init__(self, stream_id: int, attributes: dict = {}):
        super().__init__(stream_id, attributes)


class Attachment:
    def __init__(self, path: str):
        self.__path = path

    @property
    def path(self):
        return self.__path


class FontAttachment(Attachment):
    def __init__(self, path):
        super().__init__(path)
        self.__font_names = []
        self.get_font_names()

    @property
    def font_names(self):
        return self.__font_names

    def get_font_names(self):
        if self.path is None:
            return
        font = ttLib.TTFont(self.path)
        name = ""
        for record in font['name'].names:
            if record.nameID == 4:
                name = str(record)
                break
        self.__font_names.append(name)
