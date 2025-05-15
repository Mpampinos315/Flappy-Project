import math
import pygame.sprite
import assets
import configs
from layer import Layer
import time


class Bird(pygame.sprite.Sprite):
    def __init__(self, *groups, bird_type="yellow"):
        self._layer = Layer.PLAYER
        super().__init__(*groups)

        self.bird_type = bird_type

        if bird_type == "robot":
            self.images = [
                assets.get_sprite("robot-upflap"),
                assets.get_sprite("robot-midflap"),
                assets.get_sprite("robot-downflap")
            ]
            self.images = [pygame.transform.scale(img, (int(img.get_width() * 2.1),
                                                        int(img.get_height() * 2.1)))
                           for img in self.images]
        elif bird_type == "super":
            self.images = [
                assets.get_sprite("Super-upflap"),
                assets.get_sprite("Super-midflap"),
                assets.get_sprite("Super-downflap")
            ]
            self.images = [pygame.transform.scale(img, (int(img.get_width() * 2.1),
                                                        int(img.get_height() * 2.1)))
                           for img in self.images]
        else:
            self.bird_type = "yellow"
            self.images = [
                assets.get_sprite("yellowbird-upflap"),
                assets.get_sprite("yellowbird-midflap"),
                assets.get_sprite("yellowbird-downflap")
            ]

        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=(-50, 200))

        # Create collision mask and initialize vertical movement
        self.mask = pygame.mask.from_surface(self.image)
        self.flap = 0

        self.has_shield = False
        self.shield_timer = 0
        self.shield_active = False
        self.shield_effect = None

    def activate_shield(self):
        self.has_shield = True
        shield_size = max(self.rect.width, self.rect.height) + 20
        self.shield_effect = pygame.Surface((shield_size, shield_size), pygame.SRCALPHA)
        pygame.draw.circle(self.shield_effect, (0, 150, 255, 128),
                           (shield_size // 2, shield_size // 2),
                           shield_size // 2 - 2)
        if hasattr(assets, "SoundEffects") and hasattr(assets, "SoundEffects") and "powerUp" in assets.SoundEffects:
            assets.audio_play("powerUp")

    def extend_shield_after_collision(self):
        self.shield_active = True
        self.shield_timer = time.time()
        self.has_shield = False

    def update(self):
        self.images.insert(0, self.images.pop())
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.flap += configs.GRAVITY
        self.rect.y += self.flap
        if self.rect.x < 50:
            self.rect.x += 3

        # Check if shield has expired
        if self.shield_active and time.time() - self.shield_timer >= 1.0:
            self.shield_active = False
            self.shield_effect = None

        # Update shield effect if active
        if (self.has_shield or self.shield_active) and self.shield_effect is not None:
            self.shield_effect.fill((0, 0, 0, 0))

            # Calculate pulsating effect
            pulse_speed = 3.14 if not self.shield_active else 6.28
            time_factor = time.time() if not self.shield_active else (time.time() - self.shield_timer)
            alpha = int(128 + 64 * abs(math.sin(time_factor * pulse_speed)))

            shield_size = self.shield_effect.get_width()
            pygame.draw.circle(self.shield_effect, (0, 150, 255, alpha),
                               (shield_size // 2, shield_size // 2),
                               shield_size // 2 - 2)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.flap = 0
            self.flap -= 6
            assets.audio_play("wing")

    def check_collision(self, sprites):
        for sprite in sprites:
            if type(sprite).__name__ == "Floor" and self.rect.colliderect(sprite.rect):
                if self.rect.bottom >= sprite.rect.top:
                    return True

        if self.shield_active:
            return False

        # Check for column collisions
        for sprite in sprites:
            if type(sprite).__name__ == "Column":
                if pygame.sprite.collide_mask(self, sprite):
                    if self.has_shield:
                        self.extend_shield_after_collision()
                        if hasattr(assets, "SoundEffects") and hasattr(assets,"SoundEffects") and "explosion" in assets.SoundEffects:
                            assets.audio_play("explosion")
                        return False
                    else:
                        return True
        return False

    def draw(self, surface):
        surface.blit(self.image, self.rect)

        # Draw shield effect if active
        if (self.has_shield or self.shield_active) and self.shield_effect:
            shield_rect = self.shield_effect.get_rect(center=self.rect.center)
            surface.blit(self.shield_effect, shield_rect)