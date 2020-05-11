from pathlib import Path

video_files_extensions = [".mkv", ".mp4", "avi"]
audio_files_extensions = [".mka", ".aac", ".mp3"]
subtitles_files_extensions = [".srt", ".ass", ".ssa"]
attach_font_extensions = [".ttf", ".otf"]


def get_name_templates(path):
    """Scans all files in a folder and subfolders for video files returns a template dict
        
        Keyword arguments:
        path -- path to anime release

        template dict content:
        key -- video file name without extention
        val -- list
                    * absolute path
                    * empty subtitle list
                    * empty audio list
                    * empty font list
    """

    result_dict = {}

    dir = Path(path)
    for child in dir.iterdir():
        if child.is_dir():
            result_dict.update(get_name_templates(child))
        else:
            if child.suffix.lower() in video_files_extensions:
                result_dict[child.stem] = [str(child), [], [], []]
    return result_dict


def get_subtitles_from_templates(path, template_dict):
    """Scans all files in a folder and subfolders for subtitles file
        and adds information about subtitles to each template_dict entry
        
        Keyword arguments:
        path -- path to anime release
        template_dict -- template dict from get_name_templates()

        Subtitle list entity content:
        path -- path to subtitle file
        name -- subtitle label
        lang -- subtitle language label
        dispose -- mkv subtitle flag
    """

    result_dict = template_dict
    dir = Path(path)
    for child in dir.iterdir():
        if child.is_dir():
            result_dict.update(get_subtitles_from_templates(child, template_dict))
        else:
            if child.suffix.lower() in subtitles_files_extensions:
                if child.stem in result_dict:
                    subtitle_entity = [
                        str(child),
                        Path(str(child) + "/..").resolve().stem,
                        "rus",
                        0,
                    ]
                    result_dict[child.stem][1].append(subtitle_entity)
    return result_dict


def get_audio_from_templates(path, template_dict):
    """ Scans all files in a folder and subfolders for audio file
        and adds information about audio to each template_dict entry
        
        Keyword arguments:
        path -- path to anime release
        template_dict -- template dict from get_name_templates()

        Audio list entity content:
        path -- path to audio file
        name -- audio label
        lang -- audio language label
        dispose -- mkv audio flag
    """

    result_dict = template_dict
    dir = Path(path)
    for child in dir.iterdir():
        if child.is_dir():
            result_dict.update(get_audio_from_templates(child, template_dict))
        else:
            if child.suffix.lower() in audio_files_extensions:
                if child.stem in result_dict:
                    subtitle_entity = [
                        str(child),
                        Path(str(child) + "/..").resolve().stem,
                        "rus",
                        0,
                    ]
                    result_dict[child.stem][2].append(subtitle_entity)
    return result_dict


def get_font_list(path):
    """Scans all files in a folder and subfolders for font files return list of path to fonts
    
    Keyword arguments:
        path -- path to anime release
    """
    font_list = set()

    def _get_font_list(path):
        dir = Path(path)
        result_sublist = []
        for child in dir.iterdir():
            if child.is_dir():
                func_result = _get_font_list(child)
                result_sublist += func_result[0]
            else:
                if child.suffix.lower() in attach_font_extensions:
                    if not (child.name in font_list):
                        font_list.add(child.name)
                        result_sublist.append(str(child))
        return (result_sublist, font_list)

    func_result = _get_font_list(path)
    return func_result[0]


def scan_directory(path):
    """Scans all files in a folder and subfolders end return dict

        Keyword arguments:
        path -- path to anime release
        
        dict content:
        key -- video file name without extention
        val -- list
                    * absolute path
                    * subtitle list
                    * audio list 
                    * font list
    """
    result_dict = get_subtitles_from_templates(path, get_name_templates(path))
    result_dict = get_audio_from_templates(path, result_dict)
    font_list = get_font_list(path)
    for i in result_dict:
        result_dict[i][3] = font_list[:]
    return result_dict


if __name__ == "__main__":
    print("Sorry but scanus isn't executable program")
