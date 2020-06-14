from pprint import pprint

import subprocess

import argument
import scanus

search_path = input("Where should i search files? ")
save_path = input("Where should i save files? ")

directory = scanus.scan_directory(search_path)

curr_episode = 1

for episode_name in directory:
    print("Working with {}".format(episode_name))
    # choice = input("Should i add this? [y]/n ")
    episode = directory[episode_name]
    container = argument.Container()
    container.add_container(episode[0])  # mkv file
    if episode[1]:
        for audio in episode[1]:
            container.add_stream("audio", audio[0], name=audio[1], lang=audio[2])
    if episode[2]:
        for sub in episode[2]:
            container.add_stream("subtitles", sub[0], name=sub[1], lang=sub[2])
    if episode[3]:
        for font in episode[3]:
            container.add_stream("font", font)
    container.add_name(save_path + "\\" + episode_name)
    ffmpeg_command = container.compile()
    if subprocess.call(ffmpeg_command) != 0:
        print("Something is wrong!!!")
        break
