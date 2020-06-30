# найти потеряную либу для шрифтов

class FFMpegConf:
    def __init__(self):
        pass

class Container:
    def __init__(self,path):
        self.__path = path
        self.__stream_list = []
        self.__attach_list = []
    
    def compile_cmd(self,compiler = None, compiler_cong = None):
        return ""

class Stream:
    def __init__(self,path):
        self.__path = path

class Attach:
    def __init__(self,path):
        self.__path = path 

class FontAttach(Attach): 
    def __init__(self,path):
        super().__init__(path)
        self.__font_names = []

    @property
    def font_names(self):
        return self.__font_names
