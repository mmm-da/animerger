import os
import pathlib
from iso639 import languages
from ffmpeg import probe
from container import MetaContainer, StreamTypes


class Argument:
    @staticmethod
    def compile_mkv(container, **kwargs) -> str:
        result_str = "ffmpeg"

        # Input section
        for input in container.container_list:
            result_str += ' -i "{0}"'.format(input)          

        # Stream section
        stream_count = 0
        for stream in container.stream_list:
            result_str += " -map {0}:{1}".format(stream.container_id, stream.stream_id)
            # Video/Audio streams codec kwargs check
            if (stream.type == StreamTypes.VIDEO) and kwargs["video_codec"]:
                result_str += " -c {0}".format(kwargs["video_codec"])
            elif (stream.type == StreamTypes.AUDIO) and kwargs["audio_codec"]:
                result_str += " -c {0}".format(kwargs["audio_codec"])
            else:
                result_str += "-c copy"
            if stream.lang:
                result_str += " -metadata:s:{0} language={1}".format(
                    stream_count, stream.lang
                )
            stream_count += 1
        for num, font in enumerate(container.attach_list):
            result_str += ' -attach "{0}" -c copy -metadata:s:t:{1} mimetype=application/x-truetype-font'.format(
                font, num
            )
        # Addtional ffmpeg args
        if kwargs["additional_args"]:
            result_str += kwargs["additional_args"]
        # Save directory path kwargs check, if not exist save to *original_path*/merged
        save_path = ""
        if kwargs["save_path"]:
            save_path = kwargs["save_path"]
        else:
            save_path = pathlib.Path(container.container_list[0]).parent + "\merged"
            try:
                os.mkdir(save_path)
            except OSError:
                pass
        # Name template kwarg check
        result_str += ' "{}/{}"'.format(save_path, container.name) 
        return result_str

if __name__ == "__main__":
    print("Argument isn't executable module, but in Ka-52 you can start it.")