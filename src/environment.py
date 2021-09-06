import shutil
import platform
import appdirs
from constants import VERSION

class Environment:
    def __init__(self):
        self._platform = platform.platform()
        self._platform_version = platform.version()
        self._ffmpeg_path = shutil.which("ffmpeg")
        self._ffprobe_path = shutil.which("ffprobe")
        self._profile_dir = appdirs.user_config_dir("animerger", version=VERSION)

    def __repr__(self):
        platform_str = f"platform: {self.platform}\n"
        platform_version_str = f"platform version: {self.platform_version}\n"
        ffmpeg_path_str = f"FFmpeg executable path: {self.ffmpeg_path}\n"
        ffprobe_path_str = f"FFprobe executable path: {self.ffprobe_path}\n"
        profile_dir_str = f"profile dir path: {self.profile_dir}\n"
        return (
            platform_str
            + platform_version_str
            + ffmpeg_path_str
            + ffprobe_path_str
            + profile_dir_str
        )

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
    def ffprobe_path(self):
        return self._ffprobe_path

    @property
    def profile_dir(self):
        return self._profile_dir

