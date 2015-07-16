from globals import pygame
from EngineController import *


class Input(EngineController):
	def __init__(self, engine_wrapper):
		# Update the engine_wrapper:
		self.engine_wrapper = engine_wrapper

		self.events = pygame.event.get()
		self.pressed_keys = pygame.key.get_pressed()
		self.focussed_keys = pygame.key.get_focused()
		# The input module provides smoothkeys, which contains all keys pressed over the last 3 (!) frames
		self.smoothkeys = []
		self.__keyslist = [pygame.key.get_pressed() for i in range(4)]

	def update(self):
		self.events = pygame.event.get()
		self.pressed_keys = pygame.key.get_pressed()
		self.focussed_keys = pygame.key.get_focused()

		# Pop the first element
		self.__keyslist.pop(0)
		# Add a new one in the end of the list:
		self.__keyslist.append(pygame.key.get_pressed())
		# Make one single list of those 3:
		self.set_smoothkeys()
		# self.smoothkeys = map(lambda x, y, z, a: x or y or z or a, self.__keyslist[0], self.__keyslist[1], self.__keyslist[2], self.__keyslist[3])

	def set_smoothkeys(self):
		"""
		Updates the smoothkeys. Basically makes every element x of smoothkeys true if element x of keyslist[0] or
		element x of keyslist[1]... is true.
		"""
		self.smoothkeys = [0 for i in self.__keyslist[0]]
		for keylist in self.__keyslist:
			for key in range(len(keylist)):
				if keylist[key]:
					self.smoothkeys[key] = 1
