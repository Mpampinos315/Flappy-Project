import sys
import random
import time
import pygame
import json
import Button
import assets
import configs
from CharacterMenu import CharacterMenu
from assets import set_global_volume
from objects.Birb import Bird
from objects.Columns import Column
from objects.Floor import Floor
from objects.GAME_OVER import GameOverMessage
from objects.GAME_START import GameStartMessage
from objects.PickUps import Item
from objects.background import Background
from objects.score import Score


# Save System
def save_game_data(high_score, bird_skin, background_type, sound_effects_vol=0.5, music_vol=0.5, music_on=True):
    data = {
        "high_score": high_score,
        "selected_bird": bird_skin,
        "selected_background": background_type,
        "sound_effects_volume": sound_effects_vol,
        "music_volume": music_vol,
        "music_enabled": music_on
    }
    try:
        with open("save_data.json", "w") as file:
            json.dump(data, file)
    except:
        print("Error saving game data")


def load_game_data():
    try:
        with open("save_data.json", "r") as file:
            data = json.load(file)
            return data.get("high_score", 0), data.get("selected_bird", "yellow"), data.get("selected_background", "default"), data.get("sound_effects_volume", 0.5), data.get("music_volume", 0.5), data.get("music_enabled", True)
    except:
        return 0, "yellow", "default", 0.5, 0.5, True


def reset_game_data():
    try:
        import os
        if os.path.exists("save_data.json"):
            os.remove("save_data.json")

        save_game_data(0, "yellow", "default",  0.5, 0.5, True)
        return True
    except:
        print("Error resetting game data")
        return False


pygame.init()

screen = pygame.display.set_mode((configs.SCREENWIDTH, configs.SCREENHEIGHT))
clock = pygame.time.Clock()
column_create_event = pygame.USEREVENT
bird = None
running = True
gameover = False
gamestarted = False
game_paused = False
key_up_pressed = False
key_down_pressed = False
music_started = True
reset_click_handled = False
music_playing = False
game_music_loaded = False
menu_state = "main"
background_options = ["default", "night", "Jungle"]
current_background_index = 0
White = (255, 255, 255)
Black = (0, 0, 0)
Cyan = (0, 102, 102)
sound_effects_volume = 0.5
music_volume = 0.5
last_click_time = 0
click_cooldown = 300
volume = sound_effects_volume
set_global_volume(sound_effects_volume)
pygame.mixer.music.set_volume(music_volume)
small_font = pygame.font.Font("assets/UI/Fonts/Flappybird.ttf", 15)

high_score, saved_bird_skin, saved_background, sound_effects_volume, music_volume, music_enabled = load_game_data()
configs.selected_bird = saved_bird_skin
configs.selected_background = saved_background

pygame.mixer.music.load('assets/SoundEffects/IntroSong.wav')
ITEM_SPAWN_CHANCE = 0.2
items = pygame.sprite.Group()
pygame.display.set_caption("Flappy Bird")

bird_rect = pygame.Rect(100, 300, 40, 40)

assets.load_sprites()
assets.load_audios()

sprites = pygame.sprite.LayeredUpdates()

TEXT_COL = (250, 165, 0)

font = pygame.font.Font("assets/UI/Fonts/Flappybird.ttf", 45)

resume_img = pygame.image.load("assets/UI/Buttons/button_resume.png").convert_alpha()
options_img = pygame.image.load("assets/UI/Buttons/button_options.png").convert_alpha()
quit_img = pygame.image.load("assets/UI/Buttons/button_quit.png").convert_alpha()
back_img = pygame.image.load("assets/UI/Buttons/button_back.png").convert_alpha()
character_img = pygame.image.load("assets/UI/Buttons/button_character.png").convert_alpha()
audio_img = pygame.image.load("assets/UI/Buttons/button_audio.png").convert_alpha()
reset_img = pygame.image.load("assets/UI/Buttons/button_reset.png").convert_alpha()
left_arrow_img = pygame.image.load("assets/UI/Buttons/arrow_left.png").convert_alpha()
right_arrow_img = pygame.image.load("assets/UI/Buttons/arrow_right.png").convert_alpha()

resume_button = Button.Button(50, 100, resume_img, 1)
options_button = Button.Button(42, 220, options_img, 1)
quit_button = Button.Button(80, 340, quit_img, 1)
back_button = Button.Button(80, 420, back_img, 1)
character_button = Button.Button(10, 50, character_img, 0.8)
audio_button = Button.Button(10, 150, audio_img, 0.8)
reset_button = Button.Button(80, 300, reset_img, 1)
left_arrow_button = Button.Button(10, 204, left_arrow_img, 3)
right_arrow_button = Button.Button(configs.SCREENWIDTH - 100, 203, right_arrow_img, 3)

characters = [
    pygame.image.load("assets/sprites/yellowbird-midflap.png"),
    pygame.image.load("assets/sprites/robot-midflap.png"),
    pygame.image.load("assets/sprites/Super-midflap.png")
]

set_global_volume(0.5)

current_volume = assets.get_global_volume()

for i, bg in enumerate(background_options):
    if bg == configs.selected_background:
        current_background_index = i
        break


def change_background(direction):
    global current_background_index

    if direction == "left":
        current_background_index = (current_background_index - 1) % len(background_options)
    else:
        current_background_index = (current_background_index + 1) % len(background_options)

    configs.selected_background = background_options[current_background_index]
    save_game_data(high_score, configs.selected_bird, configs.selected_background)
    refresh_background()

def refresh_background():
    # Find and replace background sprites
    for sprite in sprites:
        if isinstance(sprite, Background):
            sprite.update_background_type(configs.selected_background)


# Renders the text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Calls the background & Floor
def create_sprites():
    Background(0, sprites, bg_type=configs.selected_background)
    Background(1, sprites, bg_type=configs.selected_background)

    Floor(0, sprites)
    Floor(1, sprites)

    return Bird(sprites, bird_type=configs.selected_bird), GameStartMessage(sprites), Score(sprites)


bird, game_start_message, score = create_sprites()

all_sprites = pygame.sprite.Group()


def handle_music():
    global music_playing, game_music_loaded, music_enabled

    if not music_enabled:
        if music_playing:
            pygame.mixer.music.stop()
            music_playing = False
        return
    # Control music based on game state
    if (not gamestarted and not gameover) or game_paused:
        # Play menu/start screen music if not already playing
        if not music_playing:
            pygame.mixer.music.load('assets/Music/FlappyTheme.wav')
            pygame.mixer.music.set_volume(music_volume)
            pygame.mixer.music.play(-1)
            music_playing = True
    else:
        # Switch to gameplay music
        if music_playing and pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(500)
            music_playing = False

# The main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Save data when quitting the game
            save_game_data(high_score, configs.selected_bird, configs.selected_background, sound_effects_volume, music_volume, music_enabled)
            running = False
        if event.type == pygame.KEYDOWN:
            if not game_paused:
                if event.key == pygame.K_ESCAPE:
                    save_game_data(high_score, configs.selected_bird, configs.selected_background, sound_effects_volume, music_volume, music_enabled)
                    running = False
            elif game_paused:
                if event.key == pygame.K_ESCAPE:
                    menu_state = "main"
                    game_paused = not game_paused
        if event.type == column_create_event:
            Column(sprites)
            if random.random() < ITEM_SPAWN_CHANCE:
                new_item = Item(sprites, items)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not gamestarted and not gameover and not game_paused:
                gamestarted = True
                game_start_message.kill()
                pygame.time.set_timer(column_create_event, 1500)
            if event.key == pygame.K_SPACE and gameover:
                gameover = False
                gamestarted = False
                sprites.empty()
                items.empty()
                bird, game_start_message, score = create_sprites()
            if event.key == pygame.K_m and not gamestarted:
                game_paused = not game_paused


        bird.handle_event(event)
        handle_music()

    # Process item collisions outside the loop
    if gamestarted and not gameover and not game_paused:
        if bird and hasattr(bird, 'rect'):
            item_collisions = pygame.sprite.spritecollide(bird, items, True)
        else:
            item_collisions = []
        for item in item_collisions:
            if item.type == "coin":
                score.value += 5
                if hasattr(assets, "SoundEffects") and hasattr(assets,"SoundEffects") and "coin" in assets.SoundEffects:
                    assets.audio_play("coin")
            elif item.type == "Shield2":
                bird.activate_shield()
                shield_text = font.render("SHIELD ACTIVE!", True, (0, 255, 255))
                screen.blit(shield_text, (configs.SCREENWIDTH // 2 - shield_text.get_width() // 2, 150))
                pygame.display.update()

    if not game_paused:
        screen.fill(0)
        for sprite in sprites:
            screen.blit(sprite.image, sprite.rect)
        all_sprites.draw(screen)
        items.draw(screen)
        items.update()
        if bird and (bird.has_shield or bird.shield_active):
            # Draw shield indicator
            if bird.has_shield:
                shield_text = "SHIELD ACTIVE"
                shield_color = (0, 200, 255)

            shield_indicator = font.render(shield_text, True, shield_color)
            screen.blit(shield_indicator, (configs.SCREENWIDTH - shield_indicator.get_width() - 10, 10))

            # Show remaining time if shield effect is active
            if bird.shield_active:
                time_left = max(0, 2.0 - (time.time() - bird.shield_timer))
                time_text = f"{time_left:.1f}s"
                time_indicator = font.render(time_text, True, shield_color)
                screen.blit(time_indicator, (configs.SCREENWIDTH - time_indicator.get_width() - 10, 50))

        # Checks if it's on the menu, start or quit screen and writes the correct message
        if gameover:
            draw_text("Press ESC to quit", font, TEXT_COL, 20, 180)
        elif gameover == False and not gamestarted and not game_paused:
            draw_text("Press M for Menu", font, TEXT_COL, 12, 460)
            draw_text("SPACE to Start", font, (0, 102, 102), 40, 420)

            # Display high score on the start screen
            high_score_text = f"High Score: {high_score}"
            high_score_surface = font.render(high_score_text, True, (250, 165, 0))
            screen.blit(high_score_surface, (configs.SCREENWIDTH // 2 - high_score_surface.get_width() // 2, 60))

            # Display current bird type
            bird_text = f"Bird: {configs.selected_bird.capitalize()}"
            bird_surface = font.render(bird_text, True, (250, 165, 0))
            screen.blit(bird_surface, (configs.SCREENWIDTH // 2 - bird_surface.get_width() // 2, 90))

            if left_arrow_button.draw(screen):
                change_background("left")
            if right_arrow_button.draw(screen):
                change_background("right")

            # Show unlock progress
            smaller_font = pygame.font.Font("assets/UI/Fonts/Flappybird.ttf", 20)

            if high_score < 30:
                unlock_text = f"Robot unlocks at 30 pts ({high_score}/30)"
                color = (200, 200, 200)
            elif high_score < 50:
                unlock_text = f"Super unlocks at 50 pts ({high_score}/50)"
                color = (200, 200, 200)
            else:
                unlock_text = "All characters unlocked!"
                color = (0, 255, 0)

            unlock_surface = smaller_font.render(unlock_text, True, color)
            screen.blit(unlock_surface, (configs.SCREENWIDTH // 2 - unlock_surface.get_width() // 2, 0))

        if gamestarted and not gameover:
            sprites.update()
        # Game stops and gives an option to restart or quit
        collision_detected = bird.check_collision(sprites)
        if collision_detected and not gameover:
            gameover = True
            gamestarted = False
            GameOverMessage(sprites)
            pygame.time.set_timer(column_create_event, 0)
            assets.audio_play("hit")

            if score.value > high_score:
                high_score = score.value
                save_game_data(high_score, configs.selected_bird, configs.selected_background, sound_effects_volume, music_volume, music_enabled)

        # Plays the sound and adds 1 point
        for sprite in sprites:
            if type(sprite) is Column and sprite.is_passed():
                score.value += 1
                assets.audio_play("point")

    else:
        # Menu settings and different screens
        screen.fill(Cyan)
        keys = pygame.key.get_pressed()

        # Handle menu states
        if menu_state == "main":
            if resume_button.draw(screen):
                game_paused = False
            if options_button.draw(screen):
                menu_state = "options"
            if quit_button.draw(screen):
                # Save data when quitting
                save_game_data(high_score, configs.selected_bird, configs.selected_background, sound_effects_volume, music_volume, music_enabled)
                running = False

        elif menu_state == "options":
            if back_button.draw(screen):
                menu_state = "main"
            if character_button.draw(screen):
                menu_state = "CharacterSelect"
            if audio_button.draw(screen):
                menu_state = "SoundSettings"
            if reset_button.draw(screen):
                menu_state = "ResetConfirm"

        # Character selection menu
        elif menu_state == "CharacterSelect":
            character_menu = CharacterMenu(high_score=high_score)
            character_menu.selected_bird = configs.selected_bird
            selected = False
            while not selected:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        save_game_data(high_score, configs.selected_bird, configs.selected_background, sound_effects_volume, music_volume, music_enabled)
                        pygame.quit()
                        sys.exit()

                    result = character_menu.handle_event(event)
                    if result == "back":
                        selected = True
                        menu_state = "options"
                    elif result in ["yellow", "robot", "super"]:
                        configs.selected_bird = result
                        save_game_data(high_score, configs.selected_bird, configs.selected_background, sound_effects_volume, music_volume, music_enabled)
                        selected = True
                        menu_state = "options"

                character_menu.draw(screen)
                pygame.display.flip()
                clock.tick(60)

            if bird in sprites:
                bird.kill()
            bird = Bird(sprites, bird_type=configs.selected_bird)


        elif menu_state == "SoundSettings":

            # Sound Effects Volume
            draw_text("Sound Effects", font, TEXT_COL, 20, 120)

            # Draw volume bar for sound effects
            pygame.draw.rect(screen, (100, 100, 100), (20, 160, 200, 20))
            pygame.draw.rect(screen, (0, 255, 0), (20, 160, int(sound_effects_volume * 200), 20))

            # Music Volume
            draw_text("Music", font, TEXT_COL, 20, 220)

            # Draw volume bar for music
            pygame.draw.rect(screen, (100, 100, 100), (20, 260, 200, 20))
            pygame.draw.rect(screen, (0, 255, 0), (20, 260, int(music_volume * 200), 20))

            # Music toggle button
            music_status = "ON" if music_enabled else "OFF"
            music_toggle_text = f"Music: {music_status}"
            music_toggle_surface = font.render(music_toggle_text, True, (250, 165, 0))
            music_toggle_rect = music_toggle_surface.get_rect(center=(configs.SCREENWIDTH // 2, 320))
            screen.blit(music_toggle_surface, music_toggle_rect)

            # Handle mouse interactions
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            if mouse_click[0]:
                # Sound effects volume bar
                if pygame.Rect(20, 160, 200, 20).collidepoint(mouse_pos):
                    sound_effects_volume = (mouse_pos[0] - 20) / 200
                    sound_effects_volume = max(0, min(1, sound_effects_volume))
                    set_global_volume(sound_effects_volume)

                # Music volume bar
                if pygame.Rect(20, 260, 200, 20).collidepoint(mouse_pos):
                    music_volume = (mouse_pos[0] - 20) / 200
                    music_volume = max(0, min(1, music_volume))
                    pygame.mixer.music.set_volume(music_volume)

                # Music toggle button
                if music_toggle_rect.collidepoint(mouse_pos):
                    if pygame.time.get_ticks() - last_click_time > click_cooldown:
                        music_enabled = not music_enabled
                        if music_enabled:
                            if not music_playing:
                                pygame.mixer.music.play(-1)
                                music_playing = True
                        else:
                            pygame.mixer.music.stop()
                            music_playing = False
                        last_click_time = pygame.time.get_ticks()

            if back_button.draw(screen):
                menu_state = "options"
                save_game_data(high_score, configs.selected_bird, configs.selected_background, sound_effects_volume, music_volume, music_enabled)

        elif menu_state == "ResetConfirm":
            screen.fill(Cyan)
            draw_text("Are you sure?", font, TEXT_COL, 45, 100)

            # Draw text buttons
            yes_text = font.render("YES", True, (255, 0, 0))
            yes_rect = yes_text.get_rect(center=(configs.SCREENWIDTH // 3, 250))
            screen.blit(yes_text, yes_rect)

            no_text = font.render("NO", True, (0, 255, 0))
            no_rect = no_text.get_rect(center=(configs.SCREENWIDTH * 2 // 3, 250))
            screen.blit(no_text, no_rect)

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()

            if mouse_click[0]:
                if not reset_click_handled:
                    reset_click_handled = True
                    if yes_rect.collidepoint(mouse_pos):
                        if reset_game_data():
                            high_score = 0
                            configs.selected_bird = "yellow"
                            if bird in sprites:
                                bird.kill()
                            bird = Bird(sprites, bird_type=configs.selected_bird)
                        menu_state = "options"
                    elif no_rect.collidepoint(mouse_pos):
                        menu_state = "options"
            else:
                reset_click_handled = False

    pygame.display.flip()
    clock.tick(configs.FPS)

save_game_data(high_score, configs.selected_bird, configs.selected_background, sound_effects_volume, music_volume, music_enabled)

pygame.quit()
sys.exit()