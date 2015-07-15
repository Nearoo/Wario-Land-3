import xml.etree.ElementTree as ET
from globals import pygame
from pygame.locals import *
import copy
from EngineController import *


class World(EngineController):
	"""
	Stores all level-related data like tile-position, world-collision etc.
	Before something can be done, a Tiled-levelfile must be loaded, using the "load_tmx_method.
	"""
	def __init__(self, engine_wrapper):
		# Update the engine_wrapper:
		self.engine_wrapper = engine_wrapper
		self.engine_wrapper.world = self

		self.grid_size = (1, 1) # Size of grid in amount of tiles
		self.tile_size = (1, 1) # Size of indiv. tiles

		self.tile_grid_layers = [] # All tiles of all layers are stored in this list, see self.load_tmx()
		self.tmx_root = None # Root used by ET to parse, see self.load_tmx()

		self.layer_names = ["background_color", "background", "sticky_background", "main"]

	def set_world_data(self, tile_grid_layers, grid_size, tile_size):
		self.tile_grid_layers = tile_grid_layers
		self.grid_size = grid_size
		self.tile_size = tile_size

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

		tmp_list =[]
		for layer in self.tile_grid_layers:
			for y_index in range(len(layer)):
				for x_index in range(len(layer[y_index])):
					if layer[y_index][x_index].material_group == material_group:
						# Calculate the x and y coordinates of the current tile:
						x, y = x_index*self.tile_size[0], y_index*self.tile_size[1]
						# Create a rect out of the tile and add it to the list:
						tmp_list.append(pygame.Rect((x, y), self.tile_size))
		return tmp_list
	def get_tile_relative_to(self, layer, rect, offset):
		"""Returns the material of the tile at position of rect offset with offset"""
		layer = self.get_layer_id(layer)
		y = rect.y/self.tile_size[1]+offset[0]
		x = rect.x/self.tile_size[0]+offset[1]
		# If index of wanted tile isn't there, return the first tile (should actually be a tile with no type, but World() doesn't have acces to tiles!)
		if (y > len(self.tile_grid_layers[layer])-1) or (y < 0) or (x > len(self.tile_grid_layers[layer][0])-1) or (x < 0): 
			# TODO: Find a better solution than disaster
			return self.tile_grid_layers[layer][0][0]
		else:
			return self.tile_grid_layers[layer][y][x]

	def update(self):
		pass

	def get_tile_size(self):
		"""Returns size of tiles in pixels"""
		return self.tile_size

	def get_grid_size(self):
		"""Returns gridsize in number of tiles"""
		return self.grid_size

	def get_Tile(self, layer, x, y):
		"""Returns the tile at (x, y) of layer 'layer' """
		return self.tile_grid_layers[layer][x][y]

	def get_layer_amount(self):
		"""Returns the total amount of layers"""
		return len(self.tile_grid_layers)

	def get_layer_id(self, name):
		if type(name) is int:
			return name

		else:
			return self.layer_names.index(name)