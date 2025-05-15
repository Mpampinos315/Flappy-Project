import pygame.sprite
import assets
import configs
from layer import Layer


class Background(pygame.sprite.Sprite):
    def __init__(self, position, *groups, bg_type="default"):
        self._layer = Layer.BACKGROUND
        super().__init__(*groups)

        self.bg_type = bg_type
        self.load_image()

        self.rect = self.image.get_rect(topleft=(position * configs.SCREENWIDTH, 0))

    def load_image(self):
        if self.bg_type == "night":
            original_img = assets.get_sprite("night")
        elif self.bg_type == "Jungle":
            original_img = assets.get_sprite("Jungle")
        else:
            original_img = assets.get_sprite("background")

        # Check if the image needs resizing
        if original_img.get_width() != configs.SCREENWIDTH or original_img.get_height() != configs.SCREENHEIGHT:
            self.image = pygame.transform.scale(original_img,
                                                (configs.SCREENWIDTH, configs.SCREENHEIGHT)).convert_alpha()
        else:
            self.image = original_img.convert_alpha()

    def update_background_type(self, bg_type):
        self.bg_type = bg_type
        self.load_image()

    def update(self):
        self.rect.x -= 1
        if self.rect.right <= 0:
            self.rect.left = configs.SCREENWIDTH