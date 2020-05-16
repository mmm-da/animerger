import shutil
from os import mkdir
from pathlib import Path
from random import randint
from pyunpack import Archive
from file_extentions import archive_extensions

class TempDir:
    def __init__(self, path):
        self._path = Path(path + r"/" + ".animerger-" + str(randint(1000, 9999)))
        mkdir(self._path)
        print(self._path)

    @property
    def path(self):
        return self._path

    def __del__(self):
        shutil.rmtree(self.path)

def unpack_all_archives(path, temp_path):
    """Unpacks all archives in folder and subfolders from path into temp_path
       
       Keyword arguments:
       path      -- path to anime release
       temp_path -- path to temp directory
    """
    path = Path(path)
    for i in path.iterdir():
        if i.isdir():
            unpack_all_archives(path, temp_path)
        elif i.suffix.lower() in archive_extensions:
            archive = Archive(str(i))
            archive.extractall(temp_path)
