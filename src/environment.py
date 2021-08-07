import shutil
import platform
import subprocess
import appdirs

def get_executable_version(executable_path: str, version_flag = '--version') -> str:
    process = subprocess.Popen([executable_path,version_flag], stdout=subprocess.PIPE)
    output = str()
    while process.poll() is None:
        output += process.stdout.readline()
    return output

class Environment:
    def __init__(self):
        self._platform = platform.platform()
        self._platform_version = platform.version()
        self._ffmpeg_path = shutil.which('ffmpeg')
        self._ffmpeg_version = get_executable_version(self._ffmpeg_path)
        self._ffprobe_path = shutil.which('ffprobe')
        self._ffprobe_version = get_executable_version(self._ffprobe_path)
        self._config_dir = appdirs.user_config_dir("animerger", version="0.0.2")        
        self._profile_dir = self._config_dir        

    @property
    def platform(self):
        return self._platform
    
    @property
    def platform_version(self):
        return self._platform_version

    @property
    def ffmpeg_path(self):
        return self._ffmpeg_path

    @property
    def ffmpeg_version(self):
        return self._ffmpeg_version

    @property
    def ffprobe_path(self):
        return self._ffprobe_path
    
    @property
    def ffprobe_version(self):
        return self._ffprobe_version

    @property
    def config_dir(self):
        return self._config_dir

    @property
    def profile_dir(self):
        return self._profile_dir