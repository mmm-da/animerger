from scanus import Scanus
from container import MetaContainer
from pprint import pprint
from argument import Argument
import subprocess

search_path = input("Imput dir with anume: ")

scanner = Scanus()

scanner.search_sp = False
scanner.scan_directory(search_path)

container_paths = scanner.get_container_list()
font_paths = scanner.get_font_list()

for container in container_paths:
    meta_container = MetaContainer(container, font_paths)
    subprocess.run(Argument.compile_mkv(meta_container))
    