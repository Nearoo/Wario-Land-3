from BasicComponents import *
from locals import *


class GeneralCollisionComponent(VelocityComponent):
	"""
	Handles collision with tiles that average game-actors collide with. It collides with following things:
	-solids
	-soft-break
	-hard-break
	-shot-break
	-fire-break
	"""
	def update(self, game_actor, engine):
		# Debug: Draw rects and text..
		debug_draw_rects = False
		# Debug: Draw rect-number
		debug_rect_nr = 0
		# Clear the list which stores what sides are colliding:
		colliding_sides_list = []
		game_actor.send_message(MSGN.COLLISION_SIDES, colliding_sides_list)
		# Get a copy for the rect
		rect_copy = game_actor.rect.copy()
		# Move the copy with velocity, so we can see how the rect would look like after applied velocity:
		rect_copy.move_ip(self.velocity)
		# Colliding materials:
		colliding_mats = ["solid", "soft-break", "hard-break", "shot-break", "fire-break"]
		# Get a colliding rect:
		colliding_rects = engine.world.get_colliding_rects(Layers.main, colliding_mats, rect_copy)
		# Create a velocity_multiplier with which the velocity will be multiplied in the end
		velocity_multiplier = [1, 1]

		###
		# Start algorithm:
		# For rect in colliding rects:
		for colliding_rect in colliding_rects:
			# Calculate collision-vector
			colliding_vector = self.get_collision_vector(colliding_rect, rect_copy, self.velocity)
			# If game_actor only moves in one direction and a collision happens, there's no question what
			#  component should be set to zero
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
			# Actual algorithm:
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

			# Debugging:
			if debug_draw_rects: engine.graphics.draw_rect(colliding_rect, (43, 192, 225), 2)
			# Now determine if another rect is on the side game_actor is colliding with, and if it is, ignore the collision

			# TODO: Somehow make this four very similar looking cases simpler
			if colliding_side == TOP:
				# If tile on bottom of the tile isn't in the checked material-groups:
				if engine.world.get_tile_relative_to("main", colliding_rect, (0, 1)).get_material_group() not in colliding_mats:
					velocity_multiplier[1] = 0
					# Debug:
					if debug_draw_rects:
						self.draw_debug(engine, colliding_rect, debug_rect_nr)
					# Append side of collision
					colliding_sides_list.append(colliding_side)
			elif colliding_side == BOTTOM:
				if engine.world.get_tile_relative_to("main", colliding_rect, (0, -1)).get_material_group() not in colliding_mats:
					velocity_multiplier[1] = 0
					if debug_draw_rects:
						self.draw_debug(engine, colliding_rect, debug_rect_nr)
					colliding_sides_list.append(colliding_side)
			elif colliding_side == RIGHT:
				if engine.world.get_tile_relative_to("main", colliding_rect, (-1, 0)).get_material_group() not in colliding_mats:
					velocity_multiplier[0] = 0
					if debug_draw_rects:
						self.draw_debug(engine, colliding_rect, debug_rect_nr)
					colliding_sides_list.append(colliding_side)
			elif colliding_side == LEFT:
				if engine.world.get_tile_relative_to("main", colliding_rect, (1, 0)).get_material_group() not in colliding_mats:
					velocity_multiplier[0] = 0
					if debug_draw_rects:
						self.draw_debug(engine, colliding_rect, debug_rect_nr)
					colliding_sides_list.append(colliding_side)
			debug_rect_nr += 1

		# Adjust velocity according to collision:
		self.velocity = map(lambda x, y : x*y, self.velocity, velocity_multiplier)
		# Send it to the other components:
		game_actor.send_message(MSGN.VELOCITY, self.velocity)
		# Send the colliding sides to the components:
		game_actor.send_message(MSGN.COLLISION_SIDES, colliding_sides_list)

	@staticmethod
	def draw_debug(engine, colliding_rect, rect_nr):
		engine.graphics.draw_rect(colliding_rect, (225, 0, 0), 1)
		engine.graphics.draw_text(rect_nr, colliding_rect.topleft, (225, 225, 225))

	@staticmethod
	def get_collision_vector(static_rect, mov_rect, mov_vel):
		sign = lambda x: 1 if x >= 0 else -1

		point_1 = map(lambda center, size, vel: center + 1.*size/2 * -sign(vel), static_rect.center, static_rect.size, mov_vel)
		point_2 = map(lambda center, size, vel: center + 1.*size/2 * sign(vel), mov_rect.center, mov_rect.size, mov_vel)

		return map(lambda x, y: y-x, point_1, point_2)


class GravityComponent(VelocityComponent):
	"""
	Adds gravity to the velocity vector. Simple as that.
	self.g = acceleration, self.max_fall_speed = - the maximum fall speed!
	"""
	def __init__(self):
		VelocityComponent.__init__(self)
		self.g = 1
		self.max_fall_speed = 2

	def update(self, game_actor, engine):
		if self.velocity[1] <= self.max_fall_speed:
			self.velocity = self.velocity[0], self.velocity[1] + self.g
			game_actor.send_message(MSGN.VELOCITY, self.velocity)


class ApplyVelocityComponent(VelocityComponent):
	"""
	This component is only there to move the game_actor according to velocity sent by other components.
	Since pygame-rects can only move full numbers (integers to be precise - fractions always get rounded downwards)
	the movement for e.g. 1.5 pixel per second mast me calculated separately in order to keep the .5 pixels in the movement.
	Further details are in the update-method.
	"""
	def __init__(self):
		VelocityComponent.__init__(self)
		# Use to save the fraction part of a velocity even dough pygame only moves in full steps, rounding downwards:
		self._tmp_velocity_frac = [0, 0]
		# Create function to get the sign of a number:
		self.sign = lambda x: 1 if x >= 0 else -1

	def update(self, game_actor, engine):
		# Velocity get copied in order to prevent increase into infinity:
		tmp_velocity = self.velocity

		# Then, the fraction part of the velocity (e.g. 0.5 if velocity is 2.5) gets added to the tm_velocity_frac_var:
		self._tmp_velocity_frac = map(lambda frac, vel: frac + (abs(vel)%1)*self.sign(vel), self._tmp_velocity_frac, self.velocity)

		# After that, if tmp_velocity_frac_var is bigger than one, increase the tmp-velocity:
		tmp_velocity = map(lambda frac, vel: vel+1 if frac >= 1 else vel-1 if frac <= -1 else vel, self._tmp_velocity_frac, self.velocity)

		# Then, self._tmp_velocity_frac gets again reduced to its fraction part (e.g. 1.4 becomes 0.4)
		self._tmp_velocity_frac = map(lambda frac: self.sign(frac)*(abs(frac)%1), self._tmp_velocity_frac)

		# Finally, the game_actor gets moved with the new velocity:
		game_actor.rect.move_ip(tmp_velocity)
