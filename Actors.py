from GameActor import *
import Components.WarioComponents as wc
from Components.GeneralComponents import *


class Wario(GameActor):
	def __init__(self, position, engine_wrapper):
		GameActor.__init__(self, position, engine_wrapper)
		self.rect.size = (20, 30)
		self.components = [GravityComponent(),
						wc.StatesComponent(),
						wc.LookComponent(),
						wc.MoveComponent(),
						GeneralCollisionComponent(),
						ApplyVelocityComponent()]