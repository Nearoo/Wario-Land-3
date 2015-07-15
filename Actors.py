from GameActor import *
from Components.WarioComponents import *
from Components.GeneralComponents import *


class Wario(GameActor):
	def __init__(self, position, engine_wrapper):
		GameActor.__init__(self, position, engine_wrapper)
		self.rect.size = (20, 30)
		self.components = [GravityComponent(),
						WarioStatesComponent(),
						LookComponent(),
						WarioMoveComponent(),
						SolidCollisionComponent(),
						ApplyVelocityComponent()]
