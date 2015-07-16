import xml.etree.ElementTree as ET
from globals import pygame
from pygame.locals import *
import copy
from EngineController import *
import utilities
from Tile import *


class World(EngineController):
	"""
	Stores all level-related data like tile-position, world-collision etc.
	Before something can be done, a Tiled-levelfile must be loaded, using the "load_tmx_method.
	"""

	def __init__(self, engine_wrapper):
		# Update the engine_wrapper:
		self.engine_wrapper = engine_wrapper
		self.engine_wrapper.world = self

		self.grid_size = (1, 1)  # Size of grid in amount of tiles
		self.tile_size = (1, 1)  # Size of indiv. tiles

		self.tile_grid_layers = {}  # All tiles of all layers are stored in this list, see self.load_tmx()
		self.tmx_root = None  # Root used by ET to parse, see self.load_tmx()

		self.layer_names = ["background_color", "background", "sticky_background", "main"]

		self.tile_types = {}
		self.tile_images = utilities.split_tiled_image(pygame.image.load("tileset_n1.png").convert(), (16, 16),
													   (225, 0, 225))
		self.tiles = [Tile("deco", [img]) for img in self.tile_images]

	def set_tile_size(self, tile_size):
		self.tile_size = tile_size

	def set_gid_size(self, grid_size):
		self.grid_size = grid_size

	def get_tile_by_material_group(self, material_group):
		for tile in self.tiles:
			if tile.material_group == type:
				return tile

	def get_colliding_rect(self, material_group, rect):
		"""
		Returns a the rect of a tile with the block-groupd block_group that collides with the rect redt.
		TODO: Improve this. Maybe make self.tile_grid_layers a dict that is sorted by block type, maybe add a rect to every tile, 
			add an additional abstraction layer for tiles, a class that contains images and one that contains xy coordinates?
		"""
		# First get the rects of the demanded material group
		material_group_rects = self.get_material_group_rects(material_group)
		# ...and let python do the work. Python is in C, so it's much faster than doing it in python...
		colliding_index = rect.collidelist(material_group_rects)
		return None if colliding_index == -1 else material_group_rects[colliding_index]

	def get_colliding_rects(self, material_group, rect):
		"""TODO: See self.get_colliding_rect()"""
		# First get the rects of the demanded material group
		material_group_rects = self.get_material_group_rects(material_group)
		# ...and let python do the work. Python is in C, so it's much faster than doing it in python...
		colliding_index = rect.collidelistall(material_group_rects)
		return map(lambda index: material_group_rects[index], colliding_index)

	def get_material_group_rects(self, material_group):
		"""Returns all rects of all tiles that correspond to a certain material-group material_group.
		TODO: See get_colliding_rect()"""

		material_group = [material_group] if type(material_group) != list else material_group
		tmp_list = []
		for layer in self.tile_grid_layers.values():
			for tile in layer:
				if tile.material_group in material_group:
					# Create a rect out of the tile and add it to the list:
					tmp_list.append(tile.rect)
		return tmp_list

	def get_tile_relative_to(self, layer, rect, offset):
		"""Returns the material of the tile at position of rect offset with offset"""
		layer = self.get_layer_id(layer)
		# Calculate the postion of the wanted rect:
		pos_of_wanted_rect = map(lambda x, y, z: x+y*z, rect.topleft, self.tile_size, offset)
		# Temporary: Calculate the maximum position a tile can have:
		max_pos = map(lambda x, y: x*y, self.tile_size, self.grid_size)
		# If index of wanted tile isn't there, return the first tile (should actually be a tile with no type
		if pos_of_wanted_rect[0] > max_pos[0] or pos_of_wanted_rect[0] < 0 or \
			pos_of_wanted_rect[1] > max_pos[1] or pos_of_wanted_rect[1] < 0:
			return self.get_tile_by_material_group("deco")
		else:
			return self.tile_grid_layers[layer][self.get_tile_id_by_pos(pos_of_wanted_rect)]

	def update(self):
		pass

	def get_tile_size(self):
		"""Returns size of tiles in pixels"""
		return self.tile_size

	def get_grid_size(self):
		"""Returns gridsize in number of tiles"""
		return self.grid_size

	def get_Tile(self, layer, pos_or_id):
		"""
		Returns the tile with either position or id "pos_or_id", depending on the type of pos_or_id.
		:param layer: The layer on which the tile is located
		:param pos_or_id: Either the position (tuple) or id (int) of the wanted tile-instance
		:return: Wanted tile-instance
		"""
		assert type(pos_or_id) is tuple or type(pos_or_id) is int, "Pos_or_id-argument must be either tuple or int."

		# If pos_or_id is a position:
		if type(pos_or_id) is tuple:
			# Convert tile_id from position to id:
			tile_id = self.get_tile_id_by_pos(pos_or_id)
		else:
			# Else just take pos_or_id
			tile_id = pos_or_id
		# Return the wanted tile
		return self.tile_grid_layers[layer][tile_id]

	def get_tile_id_by_pos(self, pos):
		"""
		returns a tile-id based on its position
		:param pos: The position of the wanted tile in pixels
		:return: Tile_id
		"""
		return pos[0]/self.tile_size[0]+(pos[1]/self.tile_size[1])*self.grid_size[0]

	def get_tile_pos_by_id(self, tile_id):
		"""
		Returns the position of a tile in pixels by its id
		:param tile_id: The id of the wanted tile-position
		:return: The position of the tile
		"""
		x = (tile_id % self.grid_size[0])*self.tile_size[0]
		y = (tile_id-(tile_id%self.grid_size[0]))/self.grid_size[0]*self.tile_size[1]

		return x, y

	def get_layer_amount(self):
		"""Returns the total amount of layers"""
		return len(self.tile_grid_layers)

	def get_layer_id(self, name):
		if type(name) is int:
			return name

		else:
			return self.layer_names.index(name)

	def set_tile_property(self, tile_id, property_name, property_value):
		self.tiles[tile_id].set_property(property_name, property_value)

	def create_tile(self, layer, position, size, tile_id):
		# Create new tile - copy.copy only makes a shallow copy, so animation-instance is the same as original
		new_tile = copy.copy(self.tiles[tile_id])
		new_tile.rect = pygame.Rect(position, size)
		if layer not in self.tile_grid_layers:
			self.tile_grid_layers[layer] = []
		self.tile_grid_layers[layer].append(new_tile)

	def get_grid(self):
		return self.tile_grid_layers

