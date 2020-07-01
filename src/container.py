
from fontTools import ttLib

class FFMpegConf:
    def __init__(self):
        pass

class Container:
    def __init__(self,path,attachments):
        self.__paths = path
        self.__stream_list = []
        self.__attach_list = []

    def compile_cmd(self,compiler = None, compiler_cong = None):
        return ""

    def join(self,container):
        pass

class Stream:
    """This class represents a Stream, which is a _media_ file (not a font or something)"""
    
    def __init__(self, path, id, **kwargs):
        self.__path = path
        self.__id = id
        # Set attributes of stream
        default_attr = dict(lang=None, default=None, forced=None)
        allowed_attr = default_attr.keys()
        default_attr.update(kwargs)
        self.__dict__.update((k,v) for k,v in default_attr.items() if k in allowed_attr)

    @property
    def path(self):
        return self.__path

    @property
    def id(self):
        return self.__id
    
class SubtitleStream(Stream):
    """Differs from _Stream_ in a field required_fonts"""

    def __init__(self, path, id, *kwargs):
        super().__init__(path, id, *kwargs)
        # todo: parse file and get required fonts
        self.__required_fonts = []

    @property
    def required_fonts(self):
        return self.__required_fonts

class Attach:
    def __init__(self,path):
        self.__path = path 

    @property
    def path(self):
        return self.__path

class FontAttach(Attach): 
    def __init__(self,path):
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
