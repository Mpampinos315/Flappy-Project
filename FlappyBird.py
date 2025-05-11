import pygame

import assets
import configs
from objects.Floor import Floor
from objects.background import Background

pygame.init()


screen = pygame.display.set_mode((configs.SCREENWIDTH, configs.SCREENHEIGHT))
clock = pygame.time.Clock()
running = True

assets.load_sprites()

sprites = pygame.sprite.LayeredUpdates()

Background(0, sprites)
Background(1, sprites)

Floor(0, sprites)
Floor(1, sprites)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("pink")

    sprites.draw(screen)
    sprites.update()

    pygame.display.flip()
    clock.tick(configs.FPS)

pygame.quit()