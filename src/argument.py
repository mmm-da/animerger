import os
import subprocess

from iso639 import languages
from ffmpeg import probe
from container import MetaContainer,StreamTypes
class Argument:
    @staticmethod
    def compile_mkv(container,config:dict = {},new_name = None):
        result_str = "ffmpeg"
        """Input section"""
        for input in container.container_list:
            result_str += ' -i "{0}"'.format(input)
        for input in container.attach_list:
            result_str += ' -i "{0}"'.format(input)
        """Stream sections"""
        for stream in container.stream_list:
            result_str += ' -map {0}:{1}'.format(stream.container_id,stream.stream_id)
            result_str += ' -c copy' 
            if stream.lang: result_str += ' -metadata language={0}'.format(stream.lang)
        for font in container.attach_list:
            result_str+= ' -attach "{0}"'.format(font)
        if new_name: result_str += ' "{0}"'.format(new_name)
        else: 
            new_name = list(os.path.splitext(container.container_list[0]))
            new_name[-1] = "_new"+new_name[-1]
            result_str += ' "{0}"'.format(str().join(new_name))
        return result_str
        

if __name__ == "__main__":
    print("Argument isn't executable module, but in Ka-52 you can start it.")
