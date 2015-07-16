from globals import pygame
from EngineController import *


class Input(EngineController):
	def __init__(self, engine_wrapper):
		"""
		Handles user-Input. Should only be instanced by the main-engine.
		:param engine_wrapper: The wrapper for the engine
		"""
		super(Input, self).__init__(engine_wrapper)
		self.engine_wrapper = engine_wrapper # Save engine-wrapper
		self.events = pygame.event.get() # Get pygame.events the first time
		self.pressed_keys = pygame.key.get_pressed() # Get pressed keys the first time
		self.focused_keys = pygame.key.get_focused() # Get focused keys the first time
		self.smoothkeys = [] # Create a list where the smoothkeys will be stored.
		self.__keyslist = [pygame.key.get_pressed() for i in range(4)]

	def update(self):
		"""
		Updates self.events, self.pressed_keys and self.focussed_keys and self.smoothkeys.
		"""
		self.events = pygame.event.get()
		self.pressed_keys = pygame.key.get_pressed()
		self.focused_keys = pygame.key.get_focused()

		#####
		# Update self.smoothkeys:
		# Add another keylist to the stack:
		self.__keyslist.pop(0)
		self.__keyslist.append(pygame.key.get_pressed())
		# Make one single list of those 3 in self.__keylist,
		# where every element is true if one of the three is true:
		self.smoothkeys = [0 for i in self.__keyslist[0]]
		for keylist in self.__keyslist:
			for key in range(len(keylist)):
				if keylist[key]:
					self.smoothkeys[key] = 1
