import pygame
import Button
import configs

class CharacterMenu:
    def __init__(self, high_score=0):
        # Pass high score to the menu when initializing
        self.high_score = high_score
        self.selected_bird = "yellow"

        # Define unlock thresholds
        self.unlock_thresholds = {
            "yellow": 0,
            "robot": 30,
            "super": 50
        }

        self.characters = {
            "yellow": pygame.image.load("assets/sprites/yellowbird-midflap.png"),
            "robot": pygame.image.load("assets/sprites/robot-midflap.png"),
            "super": pygame.image.load("assets/sprites/Super-midflap.png")
        }

        self.font = pygame.font.Font("assets/UI/Fonts/Flappybird.ttf", 30)
        self.small_font = pygame.font.Font("assets/UI/Fonts/Flappybird.ttf", 20)

        self.back_img = pygame.image.load("assets/UI/Buttons/button_back.png").convert_alpha()
        self.back_button = Button.Button(80, 400, self.back_img, 1)

    def draw(self, surface):
        surface.fill((0, 102, 102))

        title = self.font.render("SELECT CHARACTER", True, (250, 165, 0))
        surface.blit(title, (configs.SCREENWIDTH // 2 - title.get_width() // 2, 30))

        # Draw character options
        y_position = 100
        for bird_type, image in self.characters.items():
            # Draw character image
            img_rect = image.get_rect(midtop=(configs.SCREENWIDTH // 2, y_position))
            surface.blit(image, img_rect)

            # Draw character name
            name_text = self.font.render(bird_type.capitalize(), True, (255, 255, 255))
            surface.blit(name_text, (img_rect.right + 10, y_position))

            # Check if character is unlocked
            if self.high_score >= self.unlock_thresholds[bird_type]:
                # Highlight if this is the currently selected bird
                if bird_type == self.selected_bird:
                    pygame.draw.rect(surface, (0, 255, 0),
                                     (img_rect.left - 10, img_rect.top - 5,
                                      img_rect.width + 20, img_rect.height + 10), 3)

                status_text = self.small_font.render("Unlocked", True, (0, 255, 0))
            else:
                # Show locked with required score
                status_text = self.small_font.render(
                    f"Locked - Score {self.unlock_thresholds[bird_type]} to unlock",
                    True, (255, 0, 0))

                # Gray out the image to show it's locked
                gray_overlay = pygame.Surface((img_rect.width, img_rect.height), pygame.SRCALPHA)
                gray_overlay.fill((100, 100, 100, 150))
                surface.blit(gray_overlay, img_rect)

            # Display status below character
            surface.blit(status_text,
                         (configs.SCREENWIDTH // 2 - status_text.get_width() // 2,
                          y_position + img_rect.height + 5))

            y_position += 90  # Space between characters

        # Draw back button
        self.back_button.draw(surface)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check back button
            if self.back_button.rect.collidepoint(mouse_pos):
                return "back"

            # Check character selection
            y_position = 100
            for bird_type, image in self.characters.items():
                img_rect = image.get_rect(midtop=(configs.SCREENWIDTH // 2, y_position))

                # Only allow selection if character is unlocked
                if img_rect.collidepoint(mouse_pos) and self.high_score >= self.unlock_thresholds[bird_type]:
                    self.selected_bird = bird_type
                    return bird_type

                y_position += 90

        return None