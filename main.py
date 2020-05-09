from pathlib import Path

video_files_extensions = ['.mkv','.mp4','avi']
audio_files_extensions = ['.mka','.aac','.mp3']
subtitles_files_extensions = ['.srt','.ass','.ssa']
attach_font_extensions = ['.ttf','.otf']

def get_name_templates(path):    
    """ Scans all files in a folder and subfolders for video files returns a dict
        
        Keyword arguments:
        path -- path to anime release

        dict content:
        key -- video file name without extention
        val -- list
                    * absolute path
    """
    
    result_dict = {}

    dir = Path(path)
    for child in dir.iterdir():
        if(child.is_dir()):
            result_dict.update(get_name_templates(child))
        else:
            if child.suffix.lower() in video_files_extensions:
                result_dict[child.stem] = [str(child)]
    return result_dict

print(get_name_templates('G:\Girls und Panzer [BD] [720p]'))