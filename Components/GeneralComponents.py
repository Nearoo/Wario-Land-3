from BasicComponents import *


class SolidCollisionComponent(VelocityComponent):
	def update(self, game_actor, engine):
		# Debug: Draw rects and text..
		draw_things = True
		# Debug: Draw rect-number
		rect_nr = 0
		# Clear the list which stores what sides are colliding:
		colliding_sides_list = []
		game_actor.send_message(MSGN.COLLISION_SIDES, colliding_sides_list)
		# Get a copy for the rect
		rect_copy = game_actor.rect.copy()
		# Move the copy with velocity, so we can see how the rect would look like after applied velocity:
		rect_copy.move_ip(self.velocity)
		# Get a colliding rect:
		colliding_rects = engine.world.get_colliding_rects("solid", rect_copy)
		# Here, the side on which the game actor is colliding is stored (LEFT, RIGHT etc...)
		colliding_side = ""
		# Create a velocitry_multiplier with which the velocity will be multiplied in the end
		# (In the end because otherwise the algorythm doesn't work)
		velocity_multiplier = [1, 1]
		# For rect in colliding rects:
		for colliding_rect in colliding_rects:
			# Calculate collision-vector
			colliding_vector = self.get_collision_vector(colliding_rect, rect_copy, self.velocity)
			# If game_actor only moves in one direction and a collision happens, there's no quiestion what component sould be set to zweo
			if self.velocity[0] == 0:
				if self.velocity[1] > 0:
					colliding_side = BOTTOM
				else:
					colliding_side = TOP
			elif self.velocity[1] == 0:
				if self.velocity[0] > 0:
					colliding_side = RIGHT
				else:
					colliding_side = LEFT
			# Actual algorythm:
			elif abs(1.*self.velocity[0]/self.velocity[1]) > abs(1.*colliding_vector[0] / colliding_vector[1]):
				if self.velocity[0] > 0:
					colliding_side = RIGHT
				else:
					colliding_side = LEFT
			else: # ratio_velocity <= ratio_collision:
				if self.velocity[1] > 0:
					colliding_side = BOTTOM
				else:
					colliding_side = TOP

			if draw_things: engine.graphics.draw_rect(colliding_rect, (43, 192, 225), 2)
			# Now determine if another rect is on the side game_actor is colliding with, and if it is, ignore the collision
			if colliding_side == TOP:
				if engine.world.get_tile_relative_to("main", colliding_rect, (1, 0)).material_group != "solid":
					velocity_multiplier[1] = 0
					colliding_sides_list.append(colliding_side)
					if draw_things:
						self.draw_debug(engine, colliding_rect, rect_nr, colliding_side)
			elif colliding_side == BOTTOM:
				if engine.world.get_tile_relative_to("main", colliding_rect, (-1, 0)).material_group != "solid":
					velocity_multiplier[1] = 0
					if draw_things:
						self.draw_debug(engine, colliding_rect, rect_nr, colliding_side)
					colliding_sides_list.append(colliding_side)
			elif colliding_side == RIGHT:
				if engine.world.get_tile_relative_to("main", colliding_rect, (0, -1)).material_group != "solid":
					velocity_multiplier[0] = 0
					if draw_things:
						self.draw_debug(engine, colliding_rect, rect_nr, colliding_side)
					colliding_sides_list.append(colliding_side)
			elif colliding_side == LEFT:
				if engine.world.get_tile_relative_to("main", colliding_rect, (0, 1)).material_group != "solid":
					velocity_multiplier[0] = 0
					if draw_things:
						self.draw_debug(engine, colliding_rect, rect_nr, colliding_side)
					colliding_sides_list.append(colliding_side)
			rect_nr += 1

		self.velocity = map(lambda x, y : x*y, self.velocity, velocity_multiplier)
		game_actor.send_message(MSGN.VELOCITY, self.velocity)
		game_actor.send_message(MSGN.COLLISION_SIDES, colliding_sides_list)

	@staticmethod
	def draw_debug(engine, colliding_rect, rect_nr, colliding_side):
		colliding_sides = [TOP, LEFT, BOTTOM, RIGHT]
		engine.graphics.draw_rect(colliding_rect, (225, 0, 0), 1)
		engine.graphics.draw_text(rect_nr, colliding_rect.topleft, (225, 225, 225))

	@staticmethod
	def get_collision_vector(static_rect, mov_rect, mov_vel):
		sign = lambda x: 1 if x >= 0 else -1

		point_1 = map(lambda center, size, vel: center + 1.*size/2 * -sign(vel), static_rect.center, static_rect.size, mov_vel)
		point_2 = map(lambda center, size, vel: center + 1.*size/2 * sign(vel), mov_rect.center, mov_rect.size, mov_vel)

		return map(lambda x, y: y-x, point_1, point_2)


class GravityComponent(VelocityComponent):
	def __init__(self):
		VelocityComponent.__init__(self)
		self.g = 1
		self.max_fall_speed = 2

	def update(self, game_actor, engine):
		if self.velocity[1] <= self.max_fall_speed:
			self.velocity = self.velocity[0], self.velocity[1] + self.g
			game_actor.send_message(MSGN.VELOCITY, self.velocity)


class MoveAllDirectionsComponent(VelocityComponent):
	def update(self, game_actor, engine):
		if game_actor.input.pressed_keys[K_RIGHT]:
			self.velocity = [1, self.velocity[1]]
			game_actor.send_message(MSGN.VELOCITY, self.velocity)
		elif game_actor.input.pressed_keys[K_LEFT]:
			self.velocity = [-1, self.velocity[1]]
			game_actor.send_message(MSGN.VELOCITY, self.velocity)
		else:
			self.velocity = [0, self.velocity[1]]
			game_actor.send_message(MSGN.VELOCITY, self.velocity)

		if game_actor.input.pressed_keys[K_UP]:
			self.velocity = [self.velocity[0], -1]
			game_actor.send_message(MSGN.VELOCITY, self.velocity)
		elif game_actor.input.pressed_keys[K_DOWN]:
			self.velocity = [self.velocity[0], 1]
			game_actor.send_message(MSGN.VELOCITY, self.velocity)
		else:
			self.velocity = [self.velocity[0], 0]
			game_actor.send_message(MSGN.VELOCITY, self.velocity)


class ApplyVelocityComponent(VelocityComponent):
	"""
	This component is only there to move the game_actor according to velocity sent by other components.
	Since pygame-rects can only move full numbers (integers to be precise - fractions always get rounded downwards)
	the movement for e.g. 1.5 pixel per second mast me calculated separately in order to keep the .5 pixels in the movement.
	Furder details are in the update-method.
	"""
	def __init__(self):
		VelocityComponent.__init__(self)
		# Use to save the fraction part of a velocity even dough pygame only moves in full steps, rounding downwards:
		self._tmp_velocity_frac = [0, 0]

	def update(self, game_actor, engine):
		# First, since it's changed later on, the velocity gets copied in order to prevent a continuing increase
		# #if no other components are there to change it back:
		tmp_velocity = self.velocity

		# TODO: Get this system right.
		"""# Then, the fraction part of the velocity (e.g. 0.5 if velocity is 2.5) gets added to the tm_velocity_frac_var:
		self._tmp_velocity_frac = map(lambda frac, vel: frac + (vel%1)*self.sign(vel), self._tmp_velocity_frac, self.velocity)
		# After that, if tmp_velocity_frac_var is bigger than one (meaning if a bigger step of the rect _would_ occur if it wouldn't round everythin down)
		tmp_velocity = map(lambda frac, vel: vel+1 if frac >= 1 else vel, self._tmp_velocity_frac, self.velocity)
		# Then the whole numbers of tmp_velocity_frac get subtracted, so it needs again a fraction to get above 1 (e.g. 1.5 becomes 0.5)
		self._tmp_velocity_frac = map(lambda frac: self.sign(frac)*(frac %1), self._tmp_velocity_frac)

		# Finally move the game_actor according to the caluclated velocity:"""
		game_actor.rect.move_ip(tmp_velocity)
