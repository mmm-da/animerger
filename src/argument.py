import os
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
        """Stream sections"""
        stream_count = 0 
        for stream in container.stream_list:
            result_str += ' -map {0}:{1}'.format(stream.container_id,stream.stream_id)
            result_str += ' -c copy' 
            if stream.lang: result_str += ' -metadata:s:{0} language={1}'.format(stream_count,stream.lang)
            stream_count += 1
        for num,font in enumerate(container.attach_list):
            result_str+= ' -attach "{0}" -c copy -metadata:s:t:{1} mimetype=application/x-truetype-font'.format(font,num)
        if new_name: result_str += ' "{0}"'.format(new_name)
        else: 
            new_name = list(os.path.splitext(container.container_list[0]))
            new_name[-1] = "_new"+new_name[-1]
            result_str += ' "{0}"'.format(str().join(new_name))
        print("\n"+result_str+"\n")
        return result_str
        

if __name__ == "__main__":
    print("Argument isn't executable module, but in Ka-52 you can start it.")
