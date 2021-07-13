import os
import pathlib
from iso639 import languages
from ffmpeg import probe
from container import MetaContainer, StreamTypes


class Argument:
    @staticmethod
    def compile_mkv(container, **kwargs) -> str:
        result_str = ["ffmpeg", "-hide_banner", "-y", "-progress", "-"]

        additional_args = kwargs["additional_args"] if "additional_args" in kwargs else ""
        video_codec = kwargs["video_codec"] if "video_codec" in kwargs else None
        audio_codec = kwargs["audio_codec"] if "audio_codec" in kwargs else None
        save_path = None
        
        additional_args = additional_args.split(' ') if additional_args else None
        video_codec = video_codec.split(' ') if video_codec else None
        audio_codec = audio_codec.split(' ') if audio_codec else None
        
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
            result_str.append('-i')           
            result_str.append(f'{input}')        

        # Stream section
        stream_count = 0
        for stream in container.stream_list:
            result_str.append('-map')           
            result_str.append(f'{stream.container_id}:{stream.stream_id}')  
            # Video/Audio streams codec kwargs check
            if (stream.type == StreamTypes.VIDEO):
                if video_codec :
                    result_str.append(f'-c:{stream_count}')           
                    result_str.extend(video_codec) 
                else:
                    result_str.append(f'-c:{stream.container_id}')           
                    result_str.append('copy')           
            elif (stream.type == StreamTypes.AUDIO):
                if audio_codec :
                    result_str.append(f'-c:{stream_count}')           
                    result_str.extend(audio_codec) 
                else:
                    result_str.append(f'-c:{stream_count}')           
                    result_str.append('copy')    
            elif (stream.type == StreamTypes.SUBTITLE):
                result_str.append(f'-c:{stream_count}')           
                result_str.append('copy')    
            if stream.lang:
                result_str.append(f'-metadata:s:{stream_count}')           
                result_str.append(f'language={stream.lang}') 
            stream_count += 1
        for num, font in enumerate(container.attach_list):
            result_str.append('-attach')
            result_str.append(f'{font}')
            result_str.append(f'-c:{stream_count}')
            result_str.append('copy')
            result_str.append(f'-metadata:s:t:{num}')
            result_str.append('mimetype=application/x-truetype-font')
            stream_count += 1
        # Addtional ffmpeg args
        if additional_args:
            result_str.extend(additional_args)
        # Name template kwarg check
        result_str.append(f'{save_path}\{container.name}')
        return result_str

if __name__ == "__main__":
    print("Argument isn't executable module, but in Ka-52 you can start it.")
