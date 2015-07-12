import copy
from globals import pygame
from Animation import *

class Tile(object):
	""" Basically just a surface and the property material_group, which defines the
	behaviour of the Tile. There are following types:

	-solid: Just a normal, solid, unbreakable block.
	-none: No physics, only decoration (background mostly)

	-soft_break Breakable with the soft punch, jump and fall-attack
	-hard_break: Breakable with the hard punch, jump and fall-attack
	-shot_break: Breakable throwing an enemy (after charging up)
	-fire_break: Breakable when Wario is on fire (literally)

	-ladder: A material on which Wario can climb in all directions

	-water_still: Still water
	-water_left: Water that flows to the left
	-water_right: Water that flows to the right
	-water_up: Water that flows up
	-water_down: Water that flows down
	-water_impervious: Water that is impervious (Wario can't dive in it, only swim on top of it)

	-platform_fallthrough: A platform through which can be jumpt if coming from the bottom up
		Is also pervious in certain states of Wario.

	Note: The transparancy color is always (225, 0, 255), also called "magic-pink"
	 """
	def __init__(self, material_group, tiles_list, colorkey=(225, 0, 225), fpi = 10):
		# Set material_group (only for phyics, see claa description)
		self.material_group = material_group
		# Create the animation-instance containing all surfaces
		self.animation = Animation(tiles_list, fpi)

	def update(self):
		self.animation.update()

	def get_surface(self):
		return self.animation.get_surface()

	def get_solid(self):
		return solid

	def set_property(self, name, value):
		if name == "material_group":
			if value != "":
				self.material_group = value
