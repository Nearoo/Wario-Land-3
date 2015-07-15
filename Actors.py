from GameActor import *
from Components.WarioComponents import *
from Components.GeneralComponents import *


class Wario(GameActor):
	def __init__(self, position, input, world, graphics, sound, actors):
		GameActor.__init__(self, position, input, world, graphics, sound, actors)
		self.rect.size = (20, 30)
		self.components = [GravityComponent(),
						WarioStatesComponent(),
						LookComponent(),
						WarioMoveComponent(),
						SolidCollisionComponent(),
						ApplyVelocityComponent()]
