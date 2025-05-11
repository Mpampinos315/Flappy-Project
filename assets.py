import os
import pygame
sprites = {}
SoundEffects = {}

def load_sprites():
    path = os.path.join("assets", "sprites")
    for file in os.listdir(path):
        sprites[file.split('.')[0]] = pygame.image.load(os.path.join(path, file))


def get_sprite(name):
    return sprites[name]

def load_audios():
    path = os.path.join("assets", "SoundEffects")
    for file in os.listdir(path):
        SoundEffects[file.split('.')[0]] = pygame.mixer.Sound(os.path.join(path, file))

def audio_play(name):
    SoundEffects[name].play()


def set_global_volume(volume):
    for sound in SoundEffects.values():
        sound.set_volume(volume)

def get_global_volume():
    if SoundEffects:
        return next(iter(SoundEffects.values())).get_volume()
    else:
        return pygame.mixer.music.get_volume()