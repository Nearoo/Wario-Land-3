from GameActor import *
import Components.WarioComponents as wc
import Components.SpearheadComponents as spc
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


class SpearHead(GameActor):
	def __init__(self, position, engine_wrapper):
		super(SpearHead, self).__init__(position, engine_wrapper)
		self.rect.size = (20, 30)
		self.components = [GravityComponent(),
						   spc.StateComponent(),
						   spc.LookComponent(),
						   spc.MoveComponent(),
						   GeneralCollisionComponent(),
						   ApplyVelocityComponent()]