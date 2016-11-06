import copy
from globals import pygame


class Counter:
	"""
	Useful to count frames.
	"""
	def __init__(self, frames):
		"""
		:param frames: Target frames to count to
		"""
		self.max_frames = frames
		self.current_frame = 0

	def update(self, amount=1):
		"""
		Increase counter by  1 or more
		:param amount: Amount of frames, standard: 1
		:return: True or False, if target is reached or not
		"""
		self.current_frame += amount
		return self.evaluate()

	def evaluate(self):
		"""
		:return: True or False, if target is reached or not
		"""
		return self.current_frame >= self.max_frames

	def reset(self):
		"""
		Resets the counter
		:return: self
		"""
		self.current_frame = 0
		return self



def split_tiled_image(image, tile_size, colorkey=None):
	"""Splits a tiled image into single tiles in a return_list."""

	image_size = image.get_size()
	tmp_surface = pygame.Surface(tile_size)
	tmp_surface.set_colorkey(colorkey)
	return_list = []

	# For tilenr in y axis...
	for y in range(int(image_size[1]/tile_size[1])):
		# For tilenr in x axis...
		for x in range(int(image_size[0]/tile_size[0])):
			# ...blit the cutout at (tilenr_x*tilesize_x, tilenr_y*tilesize_y) on tmp_surface
			tmp_surface.blit(image, (0, 0), ((x*tile_size[0], y*tile_size[1]), tile_size))
			# Append a copy of tmp_surface to the return_list
			return_list.append(copy.copy(tmp_surface))
			# Fill the tmp_surface black again
			tmp_surface.fill((0, 0, 0))
	return return_list
