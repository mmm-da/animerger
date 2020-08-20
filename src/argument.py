import os
import anitopy
from iso639 import languages
from ffmpeg import probe
from container import MetaContainer,StreamTypes
class Argument:
    @staticmethod
    def compile_mkv(container,**kwargs) -> str:
        result_str = "ffmpeg"

        # Input section
        for input in container.container_list:
            result_str += ' -i "{0}"'.format(input)
        
        # Stream section
        stream_count = 0 
        for stream in container.stream_list:
            result_str += ' -map {0}:{1}'.format(stream.container_id,stream.stream_id)
            if (stream.type == StreamTypes.VIDEO) and kwargs['video_codec']:
                result_str += ' -c {0}'.format(kwargs['video_codec']) 
            elif (stream.type == StreamTypes.AUDIO) and kwargs['audio_codec']:
                result_str += ' -c {0}'.format(kwargs['audio_codec']) 
            else:
                result_str += '-c copy'
            if stream.lang: result_str += ' -metadata:s:{0} language={1}'.format(stream_count,stream.lang)
            stream_count += 1
        for num,font in enumerate(container.attach_list):
            result_str+= ' -attach "{0}" -c copy -metadata:s:t:{1} mimetype=application/x-truetype-font'.format(font,num)
        
        # Container naming section
        name_info = Argument.__parse_name(container.container_list[0])
        if kwargs['new_name']: result_str += ' "{0}"'.format(kwargs['new_name'])
        else: 
            if kwargs['name_template']:
                # TEMPLATE UNIMPLEMENTED MAGIC 
                pass
            else:
                # Default template is "Title EpNum.mkv"
                container_name = "{0} {1}.mkv".format(name_info['title'],name_info['ep_num']) 
                result_str += ' "{0}"'.format(str().join(container_name))
        return result_str

    @staticmethod
    def __parse_name(name:str) -> dict:
        anitopy_options = dict({"parse_episode_number": True, "parse_episode_title": False, "parse_file_extension": False, "parse_release_group": False})
        parse_result = anitopy.parse(name,options = anitopy_options)
        if (parse_result['anime_title'] is not None) and (parse_result['episode_number' is not None]):
            return dict({'title': parse_result['anime_title'],'ep_num': parse_result['episode_number']})
        else:
            return None

if __name__ == "__main__":
    print("Argument isn't executable module, but in Ka-52 you can start it.")
