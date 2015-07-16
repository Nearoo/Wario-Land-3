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
		# Will be used to store the currently loaded tmx-file:
		self.tmx_root = None
		# Will contain instances of every tile in use:
		self.tiles = []
		# Save the fps:
		self.fps = fps

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

		# Create pygame.Clock for fps-control
		self.CLOCK = pygame.time.Clock()

		# Load first map (temporary):
		self.load_tmx("Forest_N1_1.tmx")

		# DEBUG: Draw all ids:
		self.draw_tile_ids = False

	def update(self):
		"""Updates everything. Shold be called once per frame."""
		# Handle events:
		self.handle_events()
		# Update input:
		self.input.update()
		# Update world:
		self.world.update()
		# Draw the world:
		self.draw_world()
		# Update Game-Actors:
		self.actors.update()
		# Update screen:
		self.graphics.update()
		# Make sure engine doesn't run faster than 60 fps:
		self.CLOCK.tick(self.fps)

	def load_tmx(self, filepath):
		"""
		Loads the tmx-file 'filepath' and parses it.

		TODO: Maybe it would be better to move the part that parses tile-csv to the world-class....
		"""
		# Open and parse the tmx-file
		self.tmx_root = ET.parse('Forest_N1_1.tmx').getroot()

		# Get map-tag-attributes:
		map_attributes = self.tmx_root.attrib
		# Get grid-size (in tiles)
		grid_size = (int(map_attributes["width"]), int(map_attributes["height"]))
		self.world.set_gid_size(grid_size)
		# Get tile-size (in pixels)
		tile_size = (int(map_attributes["tilewidth"]), int(map_attributes["tileheight"]))
		self.world.set_tile_size(tile_size)
		# Get the tileset-image:
		tile_images = utilities.split_tiled_image(pygame.image.load("tileset_n1.png").convert(), (16, 16), (225, 0, 225))
		# Create Tile-instances:
		self.tiles = [Tile("deco", [img]) for img in tile_images]
		# Process them tilesets:
		for tileset in self.tmx_root.findall("tileset"):
			# Process the world-tileset:
			if tileset.attrib["name"] == "world":
				for tile in tileset.findall("tile"):
					# For property in tile:
					for property in tile.find("properties").findall("property"): 
						# Update tile-property. (What exactly is done is tile-specific.)
						self.world.set_tile_property(int(tile.attrib["id"]), property.attrib["name"], property.attrib["value"])

		# The next couple of lines try to fill following list which contains all information
		#  about what tile are where on which layer:
		tile_grid_layers = []

		# Iterate over all layers
		all_layers = self.tmx_root.findall("layer")
		for layer in range(len(all_layers)):
			# Save the raw csv-data
			csv_data = all_layers[layer].find("data").text
			# Iterate over the rows of the raw-csv-data,
			splitted_data = csv_data.split("\n")
			for row in range(len(splitted_data)):
				# Make sure the row isn't empty:
				if not splitted_data[row] == "":
					splitted_row = splitted_data[row].split(",")
					for column in range(len(splitted_row)):
						# Make sure the tile isn't empty:
						if not splitted_row[column] == "":
							# Create the tile
							position = map(lambda x, y: x*y, (column, row-1), tile_size)
							self.world.create_tile(layer, position, tile_size, int(splitted_row[column])-1)

		# Then, parse the objectgroup-layers
		self.actors = GameActorController(self.engine_wrapper)
		# For objectgroup-layer...
		for objectgroup in self.tmx_root.findall("objectgroup"):
			# If layername == "main"...
			if objectgroup.attrib["name"] == "main":
				# For every object in that layer...
				for object in objectgroup.findall("object"):
					# Spawn an instance by that name. See self.spawn_gameactor_by_name for further details.
					actor_name = object.attrib["name"]
					position = (float(object.attrib["x"]), float(object.attrib["y"])-float(object.attrib["height"]))
					self.actors.spawn_game_actor(actor_name, position, self.input, self.world, self.graphics, self.sound)
					# self.spawn_gameactor_by_name(object.attrib["name"], (float(object.attrib["x"]),
					# float(object.attrib["y"])-float(object.attrib["height"])))

	def spawn_gameactor_by_name(self, name, position):
		"""
		Spawn a gameactor by a given name. 

		TODO: Analyze following design:
		self.all_actors = {"Wario": Wario, "Spearhead": Spearhead}
		self.actors.append(self.all_actors[name](position, self.input, self.world, self.graphics))

		Much, much faster, but at the cost that no individual arguments can be passed... which actually isn't that bad... what additional argumetns are there anyway?
		"""
		if name == "Wario":
			self.actors.append(Wario(position, self.input, self.world, self.graphics))

	def handle_events(self):
		for event in self.input.events:
			if event.type == QUIT:
				pygame.quit()
				sys.exit()

	def draw_world(self):
		for layer in self.world.get_grid().values():
			for tile in layer:
				self.graphics.blit(tile.get_surface(), tile.get_rect())
