from Animation import *
from utilities import *

from pygame.locals import *
from globals import pygame

class GameActorComponent(object):
	"""
	GameActorComponents are components used by the superclass game-actor.
	They always and only perform one single task, for instance draw the sprite relative to the movement,
	or move relative to the keys pressed by the user.

	Everything they need they store themselves - if they need to communicate with each other, they can either
	send a message using game_actor.send((name, value)) or receive a message using self.recieve(message)."""

	def update(self, game_actor):
		"""Update the component.
		Everything from world to input to graphics is included in game_actor (game_actor.world etc...)"""
		pass

	def recieve_message(self, name, value):
		"""Recieve a message (a touple: (name, value)) from other components."""
		pass



class VelocityComponent(GameActorComponent):
	"""
	Can be used for inheritance for components that only listen to the message "velocity".
	"""
	def __init__(self):
		self.velocity = [0, 0]

	def recieve_message(self, name, value):
		if name == "velocity":
			self.velocity = list(value)

class StatesComponent(GameActorComponent):
	def __init__(self):
		self.colliding_sides = []
		self.state = "standing"
		self.look_direction = "right"

	def recieve_message(self, name, value):
		if name == "wario_state":
			self.state = value
		elif name == "wario_lookdirection":
			self.look_direction = value
		elif name == "colliding_sides":
			self.colliding_sides = value

class WarioMoveComponent(StatesComponent, VelocityComponent):
	def __init__(self):
		super(WarioMoveComponent, self).__init__()
		self.velocity = [0, 0]

		self.walk_speed = 1
		self.jump_speed = 3

	def recieve_message(self, name, value):
		super(WarioMoveComponent, self).recieve_message(name, value)
		if name == "velocity":
			self.velocity = value

	def update(self, game_actor):
		if (self.state == "upright-stay" or
					self.state == "crouch-stay" or
					self.state == "jump-stay" or
					self.state == "fall-stay"):
			self.velocity = 0, self.velocity[1]
		elif (self.state == "upright-move" or
				self.state == "crouch-move" or
				self.state == "jump-move" or
			  	self.state == "fall-move"):

			if self.look_direction == "right":
				self.velocity = self.walk_speed, self.velocity[1]
			else:
				self.velocity = -self.walk_speed, self.velocity[1]
		if (self.state == "jump-move") or (self.state == "jump-stay"):
			self.velocity = self.velocity[0], -3

		game_actor.send_message("velocity", self.velocity)


class WarioStatesComponent(GameActorComponent):
	def __init__(self):
		self.draw_state = True

		self.colliding_sides = []
		self.state = "upright-stay"
		self.look_direction = "right"

		self.frame_counter = 0
		self.state_stack = ["upright-stay"]

		self.state_stack_size = 10
		# How many times the state should be updated, makes it possible to go from e.g. upright-stay to crouch-move
		self.state_update_cycles = 3

		# Define custom keys:
		self.A = K_p
		self.B = K_l
		self.RIGHT = K_d
		self.LEFT = K_a
		self.DOWN = K_s
		self.UP = K_w

		# Set how long Wario can jump until the gravity takes him
		self.jump_duration = 20

	def recieve_message(self, name, value):
		if name == "wario_state":
			self.state = value

		elif name == "wario_lookdirection":
			self.look_direction = value

		elif name == "colliding_sides":
			self.colliding_sides = value

	def update(self, game_actor):
		# Update states:

		if self.state == "upright-stay":
			# Count up to 1800, (30 sec) and go to sleep if reached:
			if self.count_frames(1800, True):
				self.state = "sleep"

			elif game_actor.input.smoothkeys[self.RIGHT] or game_actor.input.smoothkeys[self.LEFT]:
				self.state = "upright-move"
			for event in game_actor.input.events:
				if event.type == KEYDOWN:
					if game_actor.input.smoothkeys[self.DOWN]:
						self.state = "crouch-stay"
						break
					elif game_actor.input.smoothkeys[self.A]:
						self.state = "jump-stay"

			if not "bottom" in self.colliding_sides:
				self.state = "fall-stay"

		elif self.state == "upright-move":
			if game_actor.input.smoothkeys[self.DOWN]:
				self.state = "crouch-move"
			elif game_actor.input.smoothkeys[self.A]:
				self.state = "jump-move"
			if not game_actor.input.smoothkeys[self.RIGHT] and not game_actor.input.smoothkeys[self.LEFT]:
				self.state = "upright-stay"

			if not "bottom" in self.colliding_sides:
				self.state = "fall-move"

		elif self.state == "sleep":
			if (game_actor.input.smoothkeys[self.DOWN] or
						game_actor.input.smoothkeys[self.UP] or
						game_actor.input.smoothkeys[self.LEFT] or
						game_actor.input.smoothkeys[self.RIGHT] or
						game_actor.input.smoothkeys[self.A] or
						game_actor.input.smoothkeys[self.B]):
				self.state = "upright-stay"

		elif self.state == "crouch-stay":
			if game_actor.input.smoothkeys[self.LEFT] or game_actor.input.smoothkeys[self.RIGHT]:
				self.state = "crouch-move"

			elif not game_actor.input.smoothkeys[self.DOWN]:
					self.state = "upright-stay"

		elif self.state == "crouch-move":
			if not game_actor.input.smoothkeys[self.DOWN]:
					self.state = "upright-move"
			elif not game_actor.input.smoothkeys[self.RIGHT] and not game_actor.input.smoothkeys[self.LEFT]:
				self.state = "crouch-stay"

		elif self.state == "jump-stay":
			if not game_actor.input.smoothkeys[self.A]:
				self.state = "fall-stay"
			elif game_actor.input.smoothkeys[self.RIGHT] or game_actor.input.smoothkeys[self.LEFT]:
					self.state = "jump-move"

			if self.state_stack[-1] == "jump-move":
				time_over = self.count_frames(self.jump_duration, False)
			else:
				time_over = self.count_frames(self.jump_duration, True)

			if time_over:
				self.state = "fall-stay"

		elif self.state == "jump-move":
			if not game_actor.input.smoothkeys[self.A]:
				self.state = "fall-move"
			elif not game_actor.input.smoothkeys[self.RIGHT] and not game_actor.input.smoothkeys[self.LEFT]:
				self.state = "jump-stay"

			if self.state_stack[-1] == "jump-stay":
				time_over = self.count_frames(self.jump_duration, False)
			else:
				time_over = self.count_frames(self.jump_duration, True)

			if time_over:
				self.state = "fall-move"

		elif self.state == "fall-stay":
			if game_actor.input.smoothkeys[self.RIGHT] or game_actor.input.smoothkeys[self.LEFT]:
				self.state = "fall-move"
			if "bottom" in self.colliding_sides:
				self.state = "upright-stay"

		elif self.state == "fall-move":
			if not game_actor.input.smoothkeys[self.RIGHT] and not game_actor.input.smoothkeys[self.LEFT]:
				self.state = "fall-stay"

			if "bottom" in self.colliding_sides:
				self.state = "upright-move"

		# Update Warios look-direction:
		for event in game_actor.input.events:
			if event.type == KEYDOWN:
				if event.key == self.RIGHT:
					self.look_direction = "right"
				elif event.key == self.LEFT:
					self.look_direction = "left"

		self.state_stack.append(self.state)
		game_actor.send_message("wario_lookdirection", self.look_direction)
		game_actor.send_message("wario_state", self.state)
		game_actor.send_message("wario_statestack", self.state_stack)
		if len(self.state_stack) > self.state_stack_size:
			self.state_stack.pop(0)

		if self.draw_state:
			game_actor.graphics.draw_text(self.state, (20, 20), (225, 0, 0))

	def count_frames(self, frame_amount, reset_if_new_state=True):
		"""Automatically counts frames to the given frame_amount.
		If the state changed recently and reset_if_new_state is True, the frame-counter is reset to 0."""
		# Increase counter by 1
		self.frame_counter += 1
		# Reset counter if state changed recently:
		if reset_if_new_state and self.state_stack[-1] != self.state:
			self.frame_counter = 0


		# If the needed amount of frames is reached, return true, otherwise false
		if self.frame_counter >= frame_amount:
			self.frame_counter = 0
			return True
		else:
			return False


class ApplyVelocityComponent(VelocityComponent):
	"""
	This component is only there to move the game_actor according to velocity sent by other components.
	Since pygame-rects can only move full numbers (integers to be precies - fractions always get rounded downwards)
	the movemnt for e.g. 1.5 pixel per second mast me calculated seperately in order to keep the .5 pixels in the movement.
	Furder details are in the update-method.
	"""
	def __init__(self):
		VelocityComponent.__init__(self)
		# Use to save the fraction part of a velocity even dough pygame only moves in full steps, rounding downwards:
		self._tmp_velocity_frac = [0, 0]

	def update(self, game_actor):
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


class KeyMovement(VelocityComponent):
	def __init__(self):
		VelocityComponent.__init__(self)
		# The speed Wario is moving with
		self.speed = 1
		self.colliding_sides_list = []
		self.jump_speed = 10

	def recieve_message(self, name, value):
		VelocityComponent.recieve_message(self, name, value)
		if name == "colliding_sides_list":
			self.colliding_sides_list = value

	def update(self, game_actor):

		# Walk right
		if game_actor.input.pressed_keys[K_RIGHT]:
			self.velocity[0] = self.speed
			game_actor.send_message("velocity", self.velocity)

		# Walk left
		elif game_actor.input.pressed_keys[K_LEFT]:
			self.velocity[0] = -self.speed
			game_actor.send_message("velocity", self.velocity)
		# Stand
		else:
			self.velocity[0] = 0
			game_actor.send_message("velocity", self.velocity)
		# Jump
		if "bottom" in self.colliding_sides_list:
			for event in game_actor.input.events:
				if event.type == KEYDOWN and event.key == K_UP:
					self.velocity[1] = -self.jump_speed
					game_actor.send_message("velocity", self.velocity)


class GravityComponent(VelocityComponent):
	def __init__(self):
		VelocityComponent.__init__(self)
		self.g = 1
		self.max_fall_speed = 2

	def update(self, game_actor):
		if self.velocity[1] <= self.max_fall_speed:
			self.velocity = self.velocity[0], self.velocity[1] + self.g
			game_actor.send_message("velocity", self.velocity)


class MoveAllDirectionsComponent(VelocityComponent):
	def update(self, game_actor):
		if game_actor.input.pressed_keys[K_RIGHT]:
			self.velocity = [1, self.velocity[1]]
			game_actor.send_message("velocity", self.velocity)
		elif game_actor.input.pressed_keys[K_LEFT]:
			self.velocity = [-1, self.velocity[1]]
			game_actor.send_message("velocity", self.velocity)
		else:
			self.velocity = [0, self.velocity[1]]
			game_actor.send_message("velocity", self.velocity)

		if game_actor.input.pressed_keys[K_UP]:
			self.velocity = [self.velocity[0], -1]
			game_actor.send_message("velocity", self.velocity)
		elif game_actor.input.pressed_keys[K_DOWN]:
			self.velocity = [self.velocity[0], 1]
			game_actor.send_message("velocity", self.velocity)
		else:
			self.velocity = [self.velocity[0], 0]
			game_actor.send_message("velocity", self.velocity)


class SolidCollisionComponent(VelocityComponent):
	def update(self, game_actor):
		# Debug: Draw rects and text..
		draw_things = True
		# Debug: Draw rect-number
		rect_nr = 0
		# Clear the list which stores what sides are colliding:
		colliding_sides_list = []
		game_actor.send_message("colliding_sides_list", colliding_sides_list)
		# Get a copy for the rect
		rect_copy = game_actor.rect.copy()
		# Move the copy with velocity, so we can see how the rect would look like after applied velocity:
		rect_copy.move_ip(self.velocity)
		# Get a colliding rect:
		colliding_rects = game_actor.world.get_colliding_rects("solid", rect_copy)
		# Here, the side on which the game actor is colliding is stored ("left", "right" etc...)
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
					colliding_side = "bottom"
				else:
					colliding_side = "top"
			elif self.velocity[1] == 0:
				if self.velocity[0] > 0:
					colliding_side = "right"
				else:
					colliding_side = "left"
			# Actual algorythm:
			elif abs(1.*self.velocity[0]/self.velocity[1]) > abs(1.*colliding_vector[0] / colliding_vector[1]):
				if self.velocity[0] > 0:
					colliding_side = "right"
				else:
					colliding_side = "left"
			else: # ratio_velocity <= ratio_collision:
				if self.velocity[1] > 0:
					colliding_side = "bottom"
				else:
					colliding_side = "top"

			if draw_things: game_actor.graphics.draw_rect(colliding_rect, (43, 192, 225), 2)
			# Now determine if another rect is on the side game_actor is colliding with, and if it is, ignore the collision
			if colliding_side == "top":
				if game_actor.world.get_tile_relative_to("main", colliding_rect, (1, 0)).material_group != "solid":
					velocity_multiplier[1] = 0
					colliding_sides_list.append(colliding_side)
					if draw_things:
						self.draw_debug(game_actor, colliding_rect, rect_nr, colliding_side)
			elif colliding_side == "bottom":
				if game_actor.world.get_tile_relative_to("main", colliding_rect, (-1, 0)).material_group != "solid":
					velocity_multiplier[1] = 0
					if draw_things:
						self.draw_debug(game_actor, colliding_rect, rect_nr, colliding_side)
					colliding_sides_list.append(colliding_side)
			elif colliding_side == "right":
				if game_actor.world.get_tile_relative_to("main", colliding_rect, (0, -1)).material_group != "solid":
					velocity_multiplier[0] = 0
					if draw_things:
						self.draw_debug(game_actor, colliding_rect, rect_nr, colliding_side)
					colliding_sides_list.append(colliding_side)
			elif colliding_side == "left":
				if game_actor.world.get_tile_relative_to("main", colliding_rect, (0, 1)).material_group != "solid":
					velocity_multiplier[0] = 0
					if draw_things:
						self.draw_debug(game_actor, colliding_rect, rect_nr, colliding_side)
					colliding_sides_list.append(colliding_side)
			rect_nr += 1

		self.velocity = map(lambda x, y : x*y, self.velocity, velocity_multiplier)
		game_actor.send_message("velocity", self.velocity)
		game_actor.send_message("colliding_sides", colliding_sides_list)

	@staticmethod
	def draw_debug(game_actor, colliding_rect, rect_nr, colliding_side):
		colliding_sides = ["top", "left", "bottom", "right"]
		game_actor.graphics.draw_rect(colliding_rect, (225, 0, 0), 1)
		game_actor.graphics.draw_text(rect_nr, colliding_rect.topleft, (225, 225, 225))
		# game_actor.graphics.draw_text(str(rect_nr)+": "+ colliding_side, (10, colliding_sides.index(colliding_side)*20+30), (225, 225, 225))

	@staticmethod
	def get_collision_vector(static_rect, mov_rect, mov_vel):
		sign = lambda x: 1 if x >= 0 else -1

		point_1 = map(lambda center, size, vel: center + 1.*size/2 * -sign(vel), static_rect.center, static_rect.size, mov_vel)
		point_2 = map(lambda center, size, vel: center + 1.*size/2 * sign(vel), mov_rect.center, mov_rect.size, mov_vel)

		return map(lambda x, y: y-x, point_1, point_2)


class WalkLookComponent(VelocityComponent):
	def __init__(self):
		VelocityComponent.__init__(self)

		# Initialize all Animation objects:
		self.animations = {
			"stand_right": Animation(split_tiled_image(pygame.image.load("images\\ANI_Wario_stand_r.png").convert_alpha(), (20, 29)), [100, 200, 100, 30]),
			"stand_left": Animation(split_tiled_image(pygame.image.load("images\\ANI_Wario_stand_r.png").convert_alpha(), (20, 29)), [100, 200, 100, 30]).make_x_mirror(),
			"walk_right": Animation(split_tiled_image(pygame.image.load("images\\ANI_Wario_walk_r.png").convert_alpha(), (24, 29)), 5),
			"walk_left":Animation(split_tiled_image(pygame.image.load("images\\ANI_Wario_walk_r.png").convert_alpha(), (24, 29)), 5).make_x_mirror(),
			"jump_right": Animation([pygame.image.load("images\\ANI_Wario_jump_r.png").convert_alpha()], 1),
			"jump_left": Animation([pygame.image.load("images\\ANI_Wario_jump_r.png").convert_alpha()], 1).make_x_mirror()}
		# Save the current animation
		self.current_animation = self.animations["stand_right"]
		# Save the last animation to check if a new animation has started:
		self.current_animation_name = "stand_right"
		# Play the current animation
		self.current_animation.play()

		# Save collision-sides
		self.colliding_sides_list = []

	def recieve_message(self, name, value):
		VelocityComponent.recieve_message(self, name, value)
		if name == "colliding_sides":
			self.colliding_sides_list = value

	def update(self, game_actor):
		if not "bottom" in self.colliding_sides_list:
			if self.velocity[0] > 0:
				if not self.current_animation_name == "jump_right":
					self.start_animation("jump_right")
			elif self.velocity[0] < 0:
				if not self.current_animation_name == "jump_left":
					self.start_animation("jump_left")
			else:
				if self.current_animation_name == "walk_left" or self.current_animation_name == "stand_left":
					self.start_animation("jump_left")
				elif self.current_animation_name == "walk_right" or self.current_animation_name == "stand_right":
					self.start_animation("jump_right")
		else:
			# If game actor is moving to the right:
			if self.velocity[0] > 0:
				# ...and current_animation isn't already walk_right:
				if not self.current_animation_name == "walk_right":
					self.start_animation("walk_right")
			# Same vice versa
			elif self.velocity[0] < 0:
				if not self.current_animation_name == "walk_left":
					self.start_animation("walk_left")
			else:
				# Else the game_actor is standing. Depending on the direction he walked before he's looking in one direction...
				if self.current_animation_name == "walk_right" or self.current_animation_name == "jump_right":
					self.start_animation("stand_right")
				elif self.current_animation_name == "walk_left" or self.current_animation_name == "jump_left":
					self.start_animation("stand_left")

		self.current_animation.update()
		# Calculate the position of the image so its midbottom is aligned with the midbottom of the game_actor
		surface_pos = self.current_animation.get_surface().get_rect(midbottom = game_actor.rect.midbottom)
		game_actor.graphics.blit(self.current_animation.get_surface(), surface_pos)

	def start_animation(self, animation_name):
		self.current_animation_name = animation_name
		self.current_animation = self.animations[animation_name]
		self.current_animation.reset()
		self.current_animation.update()