import copy
from globals import pygame


def split_tiled_image(image, tile_size, colorkey=None):
	"""Splits a tiled image into single tiles in a return_list."""
	
	image_size = image.get_size()
	tmp_surface = pygame.Surface(tile_size)
	tmp_surface.set_colorkey(colorkey)
	return_list = []

	# For tilenr in y axis...
	for y in range(image_size[1]/tile_size[1]):
		# For tilenr in x axis...
		for x in range(image_size[0]/tile_size[0]):
			# ...blit the cutout at (tilenr_x*tilesize_x, tilenr_y*tilesize_y) on tmp_surface
			tmp_surface.blit(image, (0, 0), ((x*tile_size[0], y*tile_size[1]), tile_size))
			# Append a copy of tmp_surface to the return_list
			return_list.append(copy.copy(tmp_surface))
			# Fill the tmp_surface black again
			tmp_surface.fill((0, 0, 0))
	return return_list

