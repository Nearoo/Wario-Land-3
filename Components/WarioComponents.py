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
					self.state == WarioStates.FALL_STAY or
					self.state == WarioStates.TURN):
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
				# The animation-component must handle this!!
				self.state = WarioStates.GOTO_SLEEP

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
				# The animation-component must handle this!!
				self.state = WarioStates.WAKE_UP

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

			if self.state_stack[-1] == WarioStates.JUMP_MOVE or self.state_stack[-1] == WarioStates.JUMP_STAY:
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

			if self.state_stack[-1] == WarioStates.JUMP_STAY or self.state_stack[-1] == WarioStates.JUMP_MOVE:
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
					if (self.state == WarioStates.UPRIGHT_STAY or self.state == WarioStates.UPRIGHT_MOVE or \
						self.state == WarioStates.TURN) and self.look_direction == LEFT:
						self.state = WarioStates.TURN
					else:
						self.look_direction = RIGHT
				elif event.key == self.LEFT:
					if (self.state == WarioStates.UPRIGHT_STAY or self.state == WarioStates.UPRIGHT_MOVE or \
						self.state == WarioStates.TURN) and self.look_direction == RIGHT:
						self.state = WarioStates.TURN
					else:
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


class LookComponent(StatesComponent):
	def __init__(self):
		super(LookComponent, self).__init__()

		# Initialize all Animation objects:
		self.animations = {}
		self.animations["stand_right"] = Animation(split_tiled_image(pygame.image.load("images\\ANI_Wario_stand_r.png").convert_alpha(),
				(20, 29)), [(0, 250), (1, 100), (2, 5), (1, 20), (2, 10), (1, 100)])
		self.animations["stand_left"] = self.animations["stand_right"].make_x_mirror()

		self.animations["walk_right"] = Animation(split_tiled_image(pygame.image.load("images\\ANI_Wario_walk_r.png").convert_alpha(), (24, 29)), 5)
		self.animations["walk_left"] = self.animations["walk_right"].make_x_mirror()

		self.animations["jump_right"] = Animation([pygame.image.load("images\\ANI_Wario_jump_r.png").convert_alpha()], 1)
		self.animations["jump_left"] = self.animations["jump_right"].make_x_mirror()

		# Load images for the next couple of animations:
		gotosleep_imgs = split_tiled_image(pygame.image.load("images\\ANI_Wario_gotosleep_r.png").convert_alpha(), (28, 30))

		self.animations["gotosleep_right"] = Animation(gotosleep_imgs, [(0, 15), (1, 15), (2, 15), (3, 15), (4, 15)])
		self.animations["gotosleep_left"] = self.animations["gotosleep_right"].make_x_mirror()

		self.animations["sleep_right"] = Animation(gotosleep_imgs, [(4, 30), (5, 20), (6, 100), (5, 20)])
		self.animations["sleep_left"] = self.animations["sleep_right"].make_x_mirror()

		self.animations["wakeup_right"] = Animation(gotosleep_imgs, [(4, 25), (3, 25), (2, 25), (1, 25), (0, 25)])
		self.animations["wakeup_left"] = self.animations["wakeup_right"].make_x_mirror()

		turn_around_img = split_tiled_image(pygame.image.load("images\\ANI_Wario_turn.png").convert_alpha(), (28, 29), (225, 0, 225))
		self.animations["turn_left"] = Animation(turn_around_img, [(3, 4), (2, 4), (1, 4)])
		self.animations["turn_right"] = Animation(turn_around_img, [(1, 4), (2, 4), (3, 4)])

		# Save the current animation
		self.current_animation = self.animations["stand_right"]
		# Save the last animation to check if a new animation has started:
		self.current_animation_name = "stand_right"
		# Play the current animation
		self.current_animation.play()

	def receive_message(self, name, value):
		super(LookComponent, self).receive_message(name, value)
		if name == MSGN.WARIO_LOOKDIRECTION:
			self.look_direction = value
		elif name == MSGN.WARIO_STATE:
			self.state = value

	def update(self, game_actor, engine):
		ld = "right" if self.look_direction == RIGHT else "left"

		if self.state == WarioStates.UPRIGHT_STAY:
			self.play_animation("stand_"+ld)
		elif self.state == WarioStates.UPRIGHT_MOVE:
			self.play_animation("walk_"+ld)
		elif self.state == WarioStates.FALL_MOVE or \
			self.state == WarioStates.FALL_STAY or \
			self.state == WarioStates.JUMP_MOVE or \
			self.state == WarioStates.JUMP_STAY:
			self.play_animation("jump_"+ld)

		elif self.state == WarioStates.GOTO_SLEEP:
			self.play_animation("gotosleep_"+ld)
			if self.current_animation.get_spritenr() == 4:
				self.play_animation("sleep_"+ld)
				self.state = WarioStates.SLEEP
				game_actor.send_message(MSGN.WARIO_STATE, self.state)
		elif self.state == WarioStates.WAKE_UP:
			self.play_animation("wakeup_"+ld)
			if self.current_animation.get_spritenr() == 4:
				self.play_animation("stand_"+ld)
				self.state = WarioStates.UPRIGHT_STAY
				game_actor.send_message(MSGN.WARIO_STATE, self.state)

		elif self.state == WarioStates.TURN:
			side = "left" if self.look_direction == RIGHT else "right"
			self.play_animation("turn_"+side)
			if self.current_animation.get_spritenr() == 2:
				self.look_direction = RIGHT if side == "right" else LEFT
				self.state = WarioStates.UPRIGHT_STAY
				game_actor.send_message(MSGN.WARIO_STATE, self.state)
				game_actor.send_message(MSGN.WARIO_LOOKDIRECTION, self.look_direction)

		# Update the current animation:
		self.current_animation.update()
		# Calculate the position of the image so its midbottom is aligned with the midbottom of the game_actor
		surface_pos = self.current_animation.get_surface().get_rect(midbottom = game_actor.rect.midbottom)
		# Blit the current sprite to the screen:
		engine.graphics.blit(self.current_animation.get_surface(), surface_pos)

	def play_animation(self, animation_name):
		"""Plays an animation only if the wanted animation isn't
		already playing.
		"""
		if self.current_animation_name != animation_name:
			self.current_animation_name = animation_name
			self.current_animation = self.animations[self.current_animation_name]
			self.current_animation.reset()
			self.current_animation.update()