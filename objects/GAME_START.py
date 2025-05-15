import pygame.sprite

import assets
import configs
from layer import Layer


class GameStartMessage(pygame.sprite.Sprite):
    def __init__(self, *groups):
        self._layer = Layer.UI
        self.image = assets.get_sprite("message")
        self.rect = self.image.get_rect(center = (configs.SCREENWIDTH / 2, configs.SCREENHEIGHT / 2))
        super().__init__(*groups)