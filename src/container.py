# найти потеряную либу для шрифтов

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
    def __init__(self,path):
        self.__path = path

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
