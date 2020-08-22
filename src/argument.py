import os
import pathlib
from iso639 import languages
from ffmpeg import probe
from container import MetaContainer, StreamTypes


class Argument:
    @staticmethod
    def compile_mkv(container, **kwargs) -> str:
        result_str = "ffmpeg"

        additional_args = kwargs["additional_args"] if "additional_args" in kwargs else ""
        video_codec = kwargs["video_codec"] if "video_codec" in kwargs else None
        audio_codec = kwargs["audio_codec"] if "audio_codec" in kwargs else None
        save_path = None
        # Save directory path kwargs check, if not exist save to *original_path*/merged
        if "save_path" in kwargs:
            save_path = kwargs["save_path"]
        
        if save_path is None:
            save_path = str(pathlib.Path(container.container_list[0]).parent) + "\merged"
            try:
                os.mkdir(save_path)
            except OSError:
                pass
            
        # Input section
        for input in container.container_list:
            result_str += ' -i "{0}"'.format(input)          

        # Stream section
        stream_count = 0
        for stream in container.stream_list:
            result_str += " -map {0}:{1}".format(stream.container_id, stream.stream_id)
            # Video/Audio streams codec kwargs check
            if (stream.type == StreamTypes.VIDEO):
                if video_codec :
                    result_str += " -c:{} {}".format(stream_count,video_codec)
                else:
                    result_str += " -c:{} copy".format(stream.container_id)
            elif (stream.type == StreamTypes.AUDIO):
                if audio_codec :
                    result_str += " -c:{} {}".format(stream_count,audio_codec)
                else:
                    result_str += " -c:{} copy".format(stream_count)
            elif (stream.type == StreamTypes.SUBTITLE):
                result_str+= " -c:{} copy".format(stream_count)
            if stream.lang:
                result_str += " -metadata:s:{0} language={1}".format(
                    stream_count, stream.lang
                )
            stream_count += 1
        for num, font in enumerate(container.attach_list):
            result_str += ' -attach "{}" -c:{} copy -metadata:s:t:{} mimetype=application/x-truetype-font'.format(
                font,stream_count, num
            )
            stream_count += 1
        # Addtional ffmpeg args
        if additional_args:
            result_str += additional_args
        # Name template kwarg check
        result_str += ' "{}\{}"'.format(save_path, container.name) 
        return result_str

if __name__ == "__main__":
    print("Argument isn't executable module, but in Ka-52 you can start it.")
