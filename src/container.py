from fontTools import ttLib
from ffmpeg import probe
import settings


class FFMpegConf:
    def __init__(self):
        pass


class Container:
    def __init__(self, path: str, attachments=[]):
        self.__path = path
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
                if path.rpartition[-1] in settings.subtitles_extensions:
                    subtitle_path = path
                else:
                    subtitle_path = None
                stream_instance = VideoStream(stream_id, subtitle_path, stream_attributes)
            else:
                stream_instance = Stream(stream_id, stream_attributes)
            self.__stream_list.append(stream_instance)
        self.__attach_list = []

    def compile_cmd(self, compiler=None, compiler_config=None) -> str:
        return ""

    def join(self, other):
        pass


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
        # todo: parse file and get required fonts
        self.__required_fonts = []

    @property
    def required_fonts(self):
        return self.__required_fonts


class VideoStream(Stream):

    def __init__(self, stream_id: int, attributes: dict = {}):
        super().__init__(stream_id, attributes)


class AudioStream(Stream):

    def __init__(self, stream_id: int, attributes: dict = {}):
        super().__init__(stream_id, attributes)


class Attach:
    def __init__(self, path: str):
        self.__path = path

    @property
    def path(self):
        return self.__path


class FontAttach(Attach):
    def __init__(self, path):
        super().__init__(path)
        self.__font_names = []
        self.get_font_names()

    @property
    def font_names(self):
        return self.__font_names

    def get_font_names(self):
        font = ttLib.TTFont(self.path)
        name = ""
        for record in font['name'].names:
            if record.nameID == 4:
                name = str(record)
                break
        self.__font_names.append(name)
