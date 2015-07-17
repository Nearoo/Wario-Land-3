from GameActor import *
from Animation import *


class BaseTile(GameActor):
	""" Basically just a surface and the property material_group, which defines the
	behaviour of the Tile. There are following types:

	-solid: Just a normal, solid, unbreakable block.
	-deco: No physics, only decoration (background mostly)

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

	-platform_fallthrough: A platform through which can be jumped if coming from the bottom up
		Is also pervious in certain states of Wario, like the zombie-wario.

	Note: The transparency color is always (225, 0, 255), also called "magic-pink"
	"""

	def __init__(self, position, engine, material_group, tiles_list):
		super(BaseTile, self).__init__(position, engine)
		# Set material_group (only for physics, see class description)
		self.material_group = material_group
		# Create the animation-instance containing all surfaces
		self.animation = Animation(tiles_list, 10)
		self.animation.update()
		# Create owm rect
		self.rect = pygame.Rect((0, 0), tiles_list[0].get_size())

	def set_property(self, property_name, property_value):
		if property_name == "material_group":
			self.material_group = property_value
		elif property_name == "alpha":
			for sprite in self.animation.sprites:
				sprite.set_alpha(0)

	def get_material_group(self):
		return self.material_group

	def _update(self):
		self.engine.graphics.blit(self.animation.get_surface(), self.rect)


class EmptyTile(BaseTile):
	"""
	An empty tile that doesn't blit. Used for "empty" areas with no tile.
	"""

	def __init__(self, *args, **kwargs):
		pass

	def update(self):
		pass

	def get_material_group(self):
		return "empty"
