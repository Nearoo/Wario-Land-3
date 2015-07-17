import xml.etree.ElementTree as ET
from globals import pygame
from pygame.locals import *
import copy
from EngineController import *
import utilities
from Tiles import *


class World(EngineController):
	def __init__(self, engine):
		"""
		Stores and manages all world-related data, most important of all, the tiles.
		"""
		super(World, self).__init__(engine)
		self.grid_size = (1, 1)  # Size of grid in amount of tiles
		self.tile_size = (1, 1)  # Size of indiv. tiles
		self.tile_grid_layers = {}  # All tiles of all layers are stored in this list, see self.load_tmx()
		self.tmx_root = None  # Root used by ET to parse, see self.load_tmx()
		self.layer_names = ["background_color", "background", "sticky_background", "main"]
		self.tile_images = utilities.split_tiled_image(pygame.image.load("tileset_n1.png").convert(), (16, 16),
													   (225, 0, 225))
		# Create the tiles:
		self.tiles = {i: BaseTile((0, 0), engine, "deco", [img]) for img, i in zip(self.tile_images, range(len(self.tile_images)))}
		# Add an empty tile:
		self.tiles[-1] = EmptyTile()
		self.tile_by_types = {tile.get_material_group(): [] for tile in self.tiles.values()}

	def _get_rects_with_material_group(self, layer, material_group):
		"""
		Returns all tiles of a layer that have a certain material group or multiple material group
		:param layer: The layer on which the rects should be
		:param material_group: material group or list of material-groups
		:return: List of tiles with that/these material-group/s
		"""
		# Make list out of material_group
		material_groups = [material_group] if type(material_group) is not list else material_group
		# Catch possible errors:
		assert layer in self.tile_grid_layers, "Layer %i doesn't exist." % layer

		# Create return-list
		return_list = []
		for material_group in material_groups:
			if material_group in self.tile_by_types[layer]:
				return_list.extend([self.tile_grid_layers[layer][i].rect
									for i in self.tile_by_types[layer][material_group]])

		return return_list

	def _get_tile_id_by_pos(self, pos):
		"""
		returns a tile-id based on its position
		:param pos: The position of the wanted tile in pixels
		:return: Tile_id
		"""
		return pos[0]/self.tile_size[0]+(pos[1]/self.tile_size[1])*self.grid_size[0]

	def _get_tile_pos_by_id(self, tile_id):
		"""
		Returns the position of a tile in pixels by its id
		:param tile_id: The id of the wanted tile-position
		:return: The position of the tile
		"""
		x = (tile_id % self.grid_size[0])*self.tile_size[0]
		y = (tile_id-(tile_id%self.grid_size[0]))/self.grid_size[0]*self.tile_size[1]

		return x, y

	def _get_layer_id(self, name):
		if type(name) is int:
			return name

		else:
			return self.layer_names.index(name)

	def update(self):
		for layer_index in range(len(self.tile_grid_layers)):
			for tile in self.tile_grid_layers[layer_index]:
				tile.update()

	def get_tile_by_material_group(self, material_group):
		"""
		Returns the base-tile of a material-group
		:param material_group: The material group desired
		:return: Tile-instance
		"""

		for tile in self.tiles:
			if tile.material_group == type:
				return tile
		else:
			assert material_group in self.tiles, "Material-group unknown."

	def get_colliding_rect(self, layer, material_group, rect):
		"""
		Returns a tile-instance that collides with a given rect and has a certain material_group.
		Returns None if no collision happens.
		:param layer: The layer on which the tiles should be checked.
		:param material_group: The desired material_group.
		:param rect: The colliding rect.
		:return: A tile instance that collides with the given rect.
		"""

		# Catch possible errors:
		assert layer in self.tile_by_types, "Layer does not exist."

		# First, get a list of all rects that have the desired material-group:
		rects_with_material_group = self._get_rects_with_material_group(layer, material_group)
		# ...and let pygame do the work. Pygame is in C, so it's much faster than doing it in python...
		colliding_index = rect.collidelist(rects_with_material_group)
		# Return None if no collision happens, else the colliding rect:
		return None if colliding_index == -1 else rects_with_material_group[colliding_index]

	def get_colliding_rects(self, layer, material_group, rect):
		"""
		Returns a list of tile-instances that collide with a given rect and have a certain material-group.
		Returns an empty list if no collision happens.
		:param layer: The layer on which the tiles should be checked.
		:param material_group: The desired material_group.
		:param rect: The colliding rect.
		:return: List of tile-instances that collide with the given rect
		"""
		# Catch possible errors:
		assert layer in self.tile_by_types, "Layer does not exist."

		# First get the rects of the demanded material group
		rects_with_material_group = self._get_rects_with_material_group(layer, material_group)
		# ...and let python do the work. Python is in C, so it's much faster than doing it in python...
		colliding_index = rect.collidelistall(rects_with_material_group)
		return map(lambda index: rects_with_material_group[index], colliding_index)

	def get_tile_relative_to(self, layer, rect, offset):
		"""
		Returns the tile with an offset to a given tile.
		:param layer: The layer in which the tile should be
		:param rect: The rect of the tile
		:param offset: The offset which the tile should have relative to the given rect
		:return: Tile with the offset
		"""
		layer = self._get_layer_id(layer)
		# Calculate the position of the wanted rect:
		pos_of_wanted_rect = map(lambda x, y, z: x+y*z, rect.topleft, self.tile_size, offset)
		# Calculate the maximum position a tile can have:
		max_pos = map(lambda x, y: x*y, self.tile_size, self.grid_size)
		# If wanted tile is outside the map (=doesn't exist), return a deco-tile:
		if pos_of_wanted_rect[0] > max_pos[0] or pos_of_wanted_rect[0] < 0 or \
			pos_of_wanted_rect[1] > max_pos[1] or pos_of_wanted_rect[1] < 0:
			return self.get_tile_by_material_group("deco")
		else:
			return self.tile_grid_layers[layer][self._get_tile_id_by_pos(pos_of_wanted_rect)]

	def get_tile_size(self):
		"""Returns size of tiles in pixels"""
		return self.tile_size

	def get_grid_size(self):
		"""Returns gridsize in number of tiles"""
		return self.grid_size

	def get_tile(self, layer, pos_or_id):
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
			tile_id = self._get_tile_id_by_pos(pos_or_id)
		else:
			# Else just take pos_or_id
			tile_id = pos_or_id
		# Return the wanted tile
		return self.tile_grid_layers[layer][tile_id]

	def get_layer_amount(self):
		"""
		Returns the total amount of layers
		"""
		return len(self.tile_grid_layers)

	def set_tile_property(self, tile_id, property_name, property_value):
		self.tiles[tile_id].set_property(property_name, property_value)

	def get_full_grid(self):
		return self.tile_grid_layers

	def create_tile(self, layer, position, size, tile_id):
		# Create new tile - copy.copy only makes a shallow copy, so animation-instance is the same as original
		new_tile = copy.copy(self.tiles[tile_id])
		# Update the rect of the new tile:
		new_tile.rect = pygame.Rect(position, size)
		# Create the layer if he doesn't already exist:
		if layer not in self.tile_grid_layers:
			self.tile_grid_layers[layer] = []
		# Append the new tile to this layer
		self.tile_grid_layers[layer].append(new_tile)

		# Update self.tile_by_types:
		# Get the id of the current tile (with which the tile can be accessed in self.tile_grid_layers:
		tile_id = len(self.tile_grid_layers[layer])-1
		# If layer doesn't exist, create it:
		if layer not in self.tile_by_types:
			self.tile_by_types[layer] = {}
		# If material_group doesn't exist, create it:
		if new_tile.get_material_group() not in self.tile_by_types[layer]:
			self.tile_by_types[layer][new_tile.get_material_group()] = []
		# Append tile:
		self.tile_by_types[layer][new_tile.get_material_group()].append(tile_id)

	def set_tile_size(self, tile_size):
		"""
		Set the size of every tile in the grid.
		:param tile_size: The size the grid-tiles should have
		:return: None
		"""
		self.tile_size = tile_size

	def set_gid_size(self, grid_size):
		"""
		:param grid_size: Size of grid in tiles
		:return: None
		"""
		self.grid_size = grid_size