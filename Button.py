import pygame

class Button:
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False
		self.last_click_time = 0
		self.cooldown = 300

	def draw(self, surface):
		action = False
		pos = pygame.mouse.get_pos()

		# Check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
				current_time = pygame.time.get_ticks()
				if current_time - self.last_click_time > self.cooldown:
					self.clicked = True
					self.last_click_time = current_time
					action = True

		# Reset click state if mouse button is released
		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		surface.blit(self.image, self.rect)

		return action
