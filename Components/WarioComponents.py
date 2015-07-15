from Animation import *
from utilities import *

from pygame.locals import *
from globals import pygame

from BasicComponents import *
from locals import *


class WarioMoveComponent(StatesComponent, VelocityComponent):
	def __init__(self):
		super(WarioMoveComponent, self).__init__()
		self.velocity = [0, 0]

		self.walk_speed = 1
		self.jump_speed = 3

	def receive_message(self, name, value):
		super(WarioMoveComponent, self).receive_message(name, value)
		if name == MSGN.VELOCITY:
			self.velocity = value

	def update(self, game_actor, engine):
		if (self.state == WarioStates.UPRIGHT_STAY or
					self.state == WarioStates.CROUCH_STAY or
					self.state == WarioStates.JUMP_STAY or
					self.state == WarioStates.FALL_STAY):
			self.velocity = 0, self.velocity[1]
		elif (self.state == WarioStates.UPRIGHT_MOVE or
				self.state == WarioStates.CROUCH_MOVE or
				self.state == WarioStates.JUMP_MOVE or
			  	self.state == WarioStates.FALL_MOVE):

			if self.look_direction == RIGHT:
				self.velocity = self.walk_speed, self.velocity[1]
			else:
				self.velocity = -self.walk_speed, self.velocity[1]
		if (self.state == WarioStates.JUMP_MOVE) or (self.state == WarioStates.JUMP_STAY):
			self.velocity = self.velocity[0], -3

		game_actor.send_message(MSGN.VELOCITY, self.velocity)


class WarioStatesComponent(StatesComponent):
	def __init__(self):
		self.draw_state = True

		self.colliding_sides = []
		self.state = WarioStates.UPRIGHT_STAY
		self.look_direction = RIGHT

		self.frame_counter = 0
		self.state_stack = [WarioStates.UPRIGHT_STAY]

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

	def update(self, game_actor, engine):
		# Update states:

		if self.state == WarioStates.UPRIGHT_STAY:
			# Count up to 1800, (30 sec) and go to sleep if reached:
			if self.count_frames(1800, True):
				self.state = WarioStates.SLEEP

			elif engine.input.smoothkeys[self.RIGHT] or engine.input.smoothkeys[self.LEFT]:
				self.state = WarioStates.UPRIGHT_MOVE
			for event in engine.input.events:
				if event.type == KEYDOWN:
					if engine.input.smoothkeys[self.DOWN]:
						self.state = WarioStates.CROUCH_STAY
						break
					elif engine.input.smoothkeys[self.A]:
						self.state = WarioStates.JUMP_STAY

			if not BOTTOM in self.colliding_sides:
				self.state = WarioStates.FALL_STAY

		elif self.state == WarioStates.UPRIGHT_MOVE:
			if engine.input.smoothkeys[self.DOWN]:
				self.state = WarioStates.CROUCH_MOVE
			elif engine.input.smoothkeys[self.A]:
				self.state = WarioStates.JUMP_MOVE
			if not engine.input.smoothkeys[self.RIGHT] and not engine.input.smoothkeys[self.LEFT]:
				self.state = WarioStates.UPRIGHT_STAY

			if not BOTTOM in self.colliding_sides:
				self.state = WarioStates.FALL_MOVE

		elif self.state == WarioStates.SLEEP:
			if (engine.input.smoothkeys[self.DOWN] or
						engine.input.smoothkeys[self.UP] or
						engine.input.smoothkeys[self.LEFT] or
						engine.input.smoothkeys[self.RIGHT] or
						engine.input.smoothkeys[self.A] or
						engine.input.smoothkeys[self.B]):
				self.state = WarioStates.UPRIGHT_STAY

		elif self.state == WarioStates.CROUCH_STAY:
			if engine.input.smoothkeys[self.LEFT] or engine.input.smoothkeys[self.RIGHT]:
				self.state = WarioStates.CROUCH_MOVE

			elif not engine.input.smoothkeys[self.DOWN]:
					self.state = WarioStates.UPRIGHT_STAY

		elif self.state == WarioStates.CROUCH_MOVE:
			if not engine.input.smoothkeys[self.DOWN]:
					self.state = WarioStates.UPRIGHT_MOVE
			elif not engine.input.smoothkeys[self.RIGHT] and not engine.input.smoothkeys[self.LEFT]:
				self.state = WarioStates.CROUCH_STAY

		elif self.state == WarioStates.JUMP_STAY:
			if not engine.input.smoothkeys[self.A]:
				self.state = WarioStates.FALL_STAY
			elif engine.input.smoothkeys[self.RIGHT] or engine.input.smoothkeys[self.LEFT]:
					self.state = WarioStates.JUMP_MOVE

			if self.state_stack[-1] == WarioStates.JUMP_MOVE:
				time_over = self.count_frames(self.jump_duration, False)
			else:
				time_over = self.count_frames(self.jump_duration, True)

			if time_over:
				self.state = WarioStates.FALL_STAY

		elif self.state == WarioStates.JUMP_MOVE:
			if not engine.input.smoothkeys[self.A]:
				self.state = WarioStates.FALL_MOVE
			elif not engine.input.smoothkeys[self.RIGHT] and not engine.input.smoothkeys[self.LEFT]:
				self.state = WarioStates.JUMP_STAY

			if self.state_stack[-1] == WarioStates.JUMP_STAY:
				time_over = self.count_frames(self.jump_duration, False)
			else:
				time_over = self.count_frames(self.jump_duration, True)

			if time_over:
				self.state = WarioStates.FALL_MOVE

		elif self.state == WarioStates.FALL_STAY:
			if engine.input.smoothkeys[self.RIGHT] or engine.input.smoothkeys[self.LEFT]:
				self.state = WarioStates.FALL_MOVE
			if BOTTOM in self.colliding_sides:
				self.state = WarioStates.UPRIGHT_STAY

		elif self.state == WarioStates.FALL_MOVE:
			if not engine.input.smoothkeys[self.RIGHT] and not engine.input.smoothkeys[self.LEFT]:
				self.state = WarioStates.FALL_STAY

			if BOTTOM in self.colliding_sides:
				self.state = WarioStates.UPRIGHT_MOVE

		# Update Warios look-direction:
		for event in engine.input.events:
			if event.type == KEYDOWN:
				if event.key == self.RIGHT:
					self.look_direction = RIGHT
				elif event.key == self.LEFT:
					self.look_direction = LEFT

		self.state_stack.append(self.state)
		game_actor.send_message(MSGN.WARIO_LOOKDIRECTION, self.look_direction)
		game_actor.send_message(MSGN.WARIO_STATE, self.state)
		game_actor.send_message(MSGN.WARIO_STATESTACK, self.state_stack)
		if len(self.state_stack) > self.state_stack_size:
			self.state_stack.pop(0)

		if self.draw_state:
			engine.graphics.draw_text(self.state, (20, 20), (225, 0, 0))

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


class WalkLookComponent(VelocityComponent):
	def __init__(self):
		VelocityComponent.__init__(self)

		# Initialize all Animation objects:
		self.animations = {
			"stand_right": Animation(split_tiled_image(pygame.image.load("images\\ANI_Wario_stand_r.png").convert_alpha(),
				(20, 29)), [(0, 250), (1, 100), (2, 5), (1, 20), (2, 10), (1, 100)]),
			"stand_left": Animation(split_tiled_image(pygame.image.load("images\\ANI_Wario_stand_r.png").convert_alpha(), (20, 29)), [100, 200, 100, 30]).make_x_mirror(),
			"walk_right": Animation(split_tiled_image(pygame.image.load("images\\ANI_Wario_walk_r.png").convert_alpha(), (24, 29)), 5),
			"walk_left": Animation(split_tiled_image(pygame.image.load("images\\ANI_Wario_walk_r.png").convert_alpha(), (24, 29)), 5).make_x_mirror(),
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

	def receive_message(self, name, value):
		VelocityComponent.receive_message(self, name, value)
		if name == MSGN.COLLISION_SIDES:
			self.colliding_sides_list = value

	def update(self, game_actor, engine):
		if not BOTTOM in self.colliding_sides_list:
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
		engine.graphics.blit(self.current_animation.get_surface(), surface_pos)

	def start_animation(self, animation_name):
		self.current_animation_name = animation_name
		self.current_animation = self.animations[animation_name]
		self.current_animation.reset()
		self.current_animation.update()