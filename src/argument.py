import os
import anitopy
from iso639 import languages
from ffmpeg import probe
from container import MetaContainer,StreamTypes
class Argument:
    @staticmethod
    def compile_mkv(container,config:dict = {},new_name:str = None,name_template:str = None) -> str:
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
            if name_template:
                """TEMPLATE MAGIC"""
                pass
            else:
                """ Default template - Title EpNum.mkv """
                info = Argument.__parse_name(container.container_list[0])
                new_name = "{0} {1}.mkv".format(info['title'],info['ep_num']) 
                result_str += ' "{0}"'.format(str().join(new_name))
        print("\n"+result_str+"\n")
        return result_str

    @staticmethod
    def __parse_name(name:str) -> dict:
        anitopy_options = dict({"parse_episode_number": True, "parse_episode_title": False, "parse_file_extension": False, "parse_release_group": False})
        parse_result = anitopy.parse(name,options = anitopy_options)
        return dict({'title': parse_result['anime_title'],'ep_num': parse_result['episode_number']})

if __name__ == "__main__":
    print("Argument isn't executable module, but in Ka-52 you can start it.")
