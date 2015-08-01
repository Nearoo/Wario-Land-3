from EngineController import *
from globals import pygame


class Sound(EngineController):
	def __init__(self, engine):
		super(Sound, self).__init__(engine)
		self._busy_channels = -1

	def get_sound(self, filename):
		return pygame.mixer.Sound(filename)

	def get_player(self):
		self._busy_channels += 1
		return pygame.mixer.channel(self._busy_channels)