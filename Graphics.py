from globals import pygame
from EngineController import *


class Graphics(EngineController):
	def __init__(self, engine_wrapper, screen_size):
		# Update the engine_wrapper:
		self.engine_wrapper = engine_wrapper
		self.engine_wrapper.graphics = self

		self.screen_size = screen_size
		self.SCREEN = pygame.display.set_mode(screen_size)
		self.BLACK_SCREEN = pygame.Surface(screen_size)

		self.camera_pos = [0, 0]
		self.camera_center_rect = None
		pygame.font.init()
		self.font =  pygame.font.Font("Other Resources\\Actor-Regular.ttf", 14)
		self.small_font = pygame.font.Font("Other Resources\\Actor-Regular.ttf", 7)

	def set_camera_focus(self, game_actor):
		self.camera_center_rect = game_actor.rect

	def blit(self, surface, position=(0, 0), area=None):
		self.SCREEN.blit(surface, position, area)

	def draw_rect(self, rect, color, width):
		pygame.draw.rect(self.SCREEN,color, rect, width)

	def draw_text(self, text, position, color):
		text = str(text)
		label = self.font.render(text, 1, color)
		self.SCREEN.blit(label, position)

	def draw_small_text(self, text, position, color):
		text = str(text)
		label = self.small_font.render(text, 1, color)
		self.SCREEN.blit(label, position)

	def update(self, area = None):
		# Calculate the cameras position:
		if area is not None:
			pygame.display.update(area)
		else:
			pygame.display.update()
		self.SCREEN.blit(self.BLACK_SCREEN, (0, 0))

	def get_screen(self):
		return self.SCREEN