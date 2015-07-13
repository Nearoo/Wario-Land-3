from GameActor import *
from Components.WarioComponents import *
from Components.GeneralComponents import *


class Wario(GameActor):
	def __init__(self, position, Input, World, Graphics):
		GameActor.__init__(self, position, Input, World, Graphics)
		self.rect.size = (20, 30)
		self.components = [GravityComponent(),
						   WalkLookComponent(),
						   WarioStatesComponent(),
						   WarioMoveComponent(),
						   SolidCollisionComponent(),
						   ApplyVelocityComponent()]
