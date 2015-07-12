from GameActor import *
from GameActorComponents import *
from utilities import *
from pygame.locals import *

import copy
import math

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
