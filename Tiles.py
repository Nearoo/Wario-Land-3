from GameActor import *
from Animation import *


class BaseTile(GameActor):
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
	def __init__(self, *args, **kwargs):
		pass
	def update(self):
		pass

	def get_material_group(self):
		return "empty"