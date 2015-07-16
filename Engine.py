import sys

from globals import pygame
from pygame.locals import *

from Input import *
from World import *
from Graphics import *
from Tile import *
from GameActorController import *

from Actors import *

import utilities

import xml.etree.ElementTree as ET


class EngineWrapper:
	"""
	Only exists to make it impossible for the components
	to access things of the engine they shouldn't. It only contains
	the instances of important things like input, world, or graphics.
	"""
	input = None
	world = None
	graphics = None
	sound = None
	actors = None

class Engine:
	def __init__(self, screen_size, fps):
		self._tmx_root = None  # Will be used to store the currently loaded tmx-file:
		self._fps = fps # Save fps
		self._CLOCK = pygame.time.Clock() # Create pygame.Clock for fps-control
		self._draw_tile_ids = False # DEBUG: Draw all ids:

		# Create the engine-wrapper:
		self.engine_wrapper = EngineWrapper
		# Create instance of Graphics-Engine:
		self.graphics = Graphics(self.engine_wrapper,screen_size)
		# Create instance of World:
		self.world = World(self.engine_wrapper)
		# Create instance of input-engine
		self.input = Input(self.engine_wrapper)
		# Create actors-controller
		self.actors = GameActorController(self.engine_wrapper)
		# Create sound-controller (not jet programmed...)
		self.sound = None

		# Update references of engine_wrapper:
		self.engine_wrapper.graphics = self.graphics
		self.engine_wrapper.world = self.world
		self.engine_wrapper.actors = self.actors
		self.engine_wrapper.input = self.input
		self.engine_wrapper.sound = self.sound

		# Finally, first map (temporary):
		self._load_tmx("Forest_N1_1.tmx")

	def update(self):
		"""
		Updates everything. Should be called once per frame.
		"""
		# Handle events:
		self._handle_events()
		# Update input:
		self.input.update()
		# Update world:
		self.world.update()
		# Draw the world:
		self._draw_world()
		# Update Game-Actors:
		self.actors.update()
		# Update screen:
		self.graphics.update()
		# Make sure engine doesn't run faster than 60 fps:
		self._CLOCK.tick(self._fps)

	def _load_tmx(self, filepath):
		"""
		Loads the tmx-file 'filepath' and parses it.

		TODO: Maybe it would be better to move the part that parses tile-csv to the world-class....
		"""

		# Empty self.actors:
		self.actors = GameActorController(self.engine_wrapper)
		# TODO: Find a way to empty self.world

		# Open and parse the tmx-file
		self._tmx_root = ET.parse('Forest_N1_1.tmx').getroot()

		# Get grid-size (in tiles)
		grid_size = (int(self._tmx_root.attrib["width"]), int(self._tmx_root.attrib["height"]))
		# Set the grid-size in the world:
		self.world.set_gid_size(grid_size)

		# Get tile-size (in pixels)
		tile_size = (int(self._tmx_root.attrib["tilewidth"]), int(self._tmx_root.attrib["tileheight"]))
		# Set the tile-size in the world:
		self.world.set_tile_size(tile_size)

		######
		# Next, process the tilesets:
		# For tileset..
		for tileset in self._tmx_root.findall("tileset"):
			# If tileset is "world":
			if tileset.attrib["name"] == "world":
				# Dor tile in this tileset:
				for tile in tileset.findall("tile"):
					# For property in tile:
					for property in tile.find("properties").findall("property"): 
						# Update tile-property
						self.world.set_tile_property(int(tile.attrib["id"]), property.attrib["name"], property.attrib["value"])

		######
		# Next, process the layers: Where is what tile?
		# For every layer...
		all_layers = self._tmx_root.findall("layer")
		for layer in range(len(all_layers)):
			# Get and save the raw csv data which contains information about where which tile is:
			csv_data = all_layers[layer].find("data").text
			# First, split the csv in rows:
			splitted_data = csv_data.split("\n")
			# For row in csv_data:
			for row in range(len(splitted_data)):
				# Make sure the row isn't empty:
				if not splitted_data[row] == "":
					splitted_row = splitted_data[row].split(",")
					# For column in csv_data (= for tile)
					for column in range(len(splitted_row)):
						# Make sure the tile isn't empty:
						if not splitted_row[column] == "":
							# Calculate the position of the tile:
							position = map(lambda x, y: x*y, (column, row-1), tile_size)
							# Finally create the tile:
							self.world.create_tile(layer, position, tile_size, int(splitted_row[column])-1)

		#####
		# Next, process object-group-layers:
		# For object-group-layer...
		for objectgroup in self._tmx_root.findall("objectgroup"):
			# If layer-name == "main"...
			if objectgroup.attrib["name"] == "main":
				# For every object in that layer...
				for object in objectgroup.findall("object"):
					# Get the name of that object (=GameActor):
					actor_name = object.attrib["name"]
					# Get the position of that object
					position = (float(object.attrib["x"]), float(object.attrib["y"])-float(object.attrib["height"]))
					# Spawn a game-actor with that name:
					self.actors.spawn_game_actor(actor_name, position, self.input, self.world, self.graphics, self.sound)

	def _handle_events(self):
		for event in self.input.events:
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

	def _draw_world(self):
		for layer in self.world.get_full_grid().values():
			for tile in layer:
				self.graphics.blit(tile.get_surface(), tile.get_rect())
