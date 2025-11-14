from settings import *
from os import walk, name
from os.path import join

def frames_loader(*path):
    #load surfaces into a dictionary with folder names as keys
    OS_name = name
    frames = {}
    for folder_path, _folders, files in walk(resource_path(join(*path))):
        folder_name = folder_path.split('\\' if OS_name == "nt" else '/')[-1]
        frames[folder_name] = []

        for file in sorted(files, key = lambda name: int(name.split(".")[0])):
            full_path = join(folder_path, file)
            frames[folder_name].append(pygame.image.load(full_path).convert_alpha())

    return frames

def audio_loader(*path):
    audio = {}
    for folder_path, _folders, file_names in walk(resource_path(join(*path))):
        for file_name in file_names:
            audio[file_name.split('.')[0]] = pygame.mixer.Sound(join(folder_path, file_name))
    return audio
