import pygame
import random
import assets
from configs import SCREENWIDTH, SCREENHEIGHT
from layer import Layer

class Item(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)

        self._layer = Layer.PLAYER + 1
        self.type = random.choice(["coin", "Shield2"])

        original_image = assets.get_sprite(f"{self.type}")
        scale_factor = 0.3
        new_width = int(original_image.get_width() * scale_factor)
        new_height = int(original_image.get_height() * scale_factor)
        self.image = pygame.transform.scale(original_image, (new_width, new_height))
        self.rect = self.image.get_rect()

        # Find active columns to position item properly
        columns = [sprite for sprite in pygame.sprite.Group(*groups)
                   if isinstance(sprite, type) and sprite.__name__ == "Column"]

        # Position item on the right side of screen
        self.rect.x = SCREENWIDTH + random.randint(20, 50)

        floor_height = assets.get_sprite("floor").get_rect().height
        min_y = 150
        max_y = SCREENHEIGHT - floor_height - 150
        self.rect.y = random.randint(min_y, max_y)

        # Movement properties (match column speed)
        self.move_speed = 2  # Same as column speed
        self.float_speed = 0.5
        self.float_direction = 1

    def update(self):
        # Move horizontally (left)
        self.rect.x -= self.move_speed

        # Subtle floating up/down movement
        self.rect.y += self.float_speed * self.float_direction
        if random.random() < 0.01:
            self.float_direction *= -1

        # Remove when off-screen
        if self.rect.right < 0:
            self.kill()