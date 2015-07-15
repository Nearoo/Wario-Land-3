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
		# Get gridsize (in tiles)
		grid_size = (int(map_attributes["width"]), int(map_attributes["height"]))
		# Get tilesize (in pixels)
		tile_size = (int(map_attributes["tilewidth"]), int(map_attributes["tileheight"]))
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
						# Update tile-property. (What exactly is done is class-specific.)
						self.tiles[int(tile.attrib["id"])].set_property(property.attrib["name"], property.attrib["value"])

		# The next coupple of lines try to fill following list which contains all information
		#  about what tile are where on which layer:
		tile_grid_layers = []

		# Iterate over all layers
		for layer in self.tmx_root.findall("layer"):
			# Save the raw csv-data
			csv_data = layer.find("data").text
			# Create a tmp-list representing one layer
			tmp_list = []
			# Iterate over the rows of the raw-csv-data,
			for row in csv_data.split("\n"):
				# Make sure no empty lists get appended
				if not row == "":
					splitted_row = row.split(",")
					# Make sure again no empty elements get appended
					if not splitted_row[-1] == "":
						# Append x row
						tmp_list.append(splitted_row)
					else:
						# Append x row
						tmp_list.append(splitted_row[:-1])
			
			# Add the tmplist as a whole to the tile_grid_layers-var
			tile_grid_layers.append(tmp_list)

			# In the end, the layer looks like this (tuples represent coords of tiles): [[(1, 0), (2, 0), (3, 0), (4, 0) ...], [(1, 1), (2, 1)...]...]
			# Or, expressed differently: [[x-axis-1], [x-axis-2]...]

		# Iterate again over all elements of self.tile_grid_layers
		for layer in range(len(tile_grid_layers)):
			for y in range(len(tile_grid_layers[layer])):
				for x in range(len(tile_grid_layers[layer][y])):
					# Exchange each element (each an int) with its corresponding tile-object
					tile_grid_layers[layer][y][x] = self.tiles[int(tile_grid_layers[layer][y][x])-1]

		# Finally pass this list to the world:
		self.world.set_world_data(tile_grid_layers, grid_size, tile_size)

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
					# self.spawn_gameactor_by_name(object.attrib["name"], (float(object.attrib["x"]), float(object.attrib["y"])-float(object.attrib["height"])))

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
		for layer in range(self.world.get_layer_amount()):
			for x in range(self.world.get_grid_size()[0]):
				for y in range(self.world.get_grid_size()[1]):
					position = (x*self.world.get_tile_size()[0], y*self.world.get_tile_size()[1])
					self.graphics.blit(self.world.get_Tile(layer, y, x).get_surface(), position)
					if self.draw_tile_ids: self.graphics.draw_small_text(y*self.world.get_grid_size()[0]+x, position, (225, 225, 225),)
