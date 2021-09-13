import yaml
from constants import PROFILE_FILENAME

from environment import Environment

def get_profiles(environment : Environment):
    profiles = dict()
    profile_dir = environment.profile_dir
    try:
        with open(profile_dir+'/'+PROFILE_FILENAME,"r") as file:
            profiles = yaml.load(file)
            print(profiles)
    except FileExistsError:
        create_profiles(environment)
    return profiles

def create_profiles(environment: Environment):
    profile_dir = environment.profile_dir
    with open(profile_dir+'/'+PROFILE_FILENAME,"x") as file:
        default_profile = {
            "default" :{
                "verbose": 1,
                "recursive": False,
                "dry_run": False,
                "guess_title": False,
                "video_codec_args": None,
                "audio_codec_args": None,
                "other_args": None,
                "output": "./merged",
            }
        }
        file.write(yaml.dump(default_profile))