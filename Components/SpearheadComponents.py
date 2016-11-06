from .BasicComponents import *
from .locals import *

from os.path import join as j_path

class StateComponent(StatesComponent, VelocityComponent):

	def __init__(self):
		super(StateComponent, self).__init__()
		self.state = ShStates.MOVE

		# Create sensor-rects. Their values aren't definitive - they're updated in the update-method.
		# Sensor-rects are rects that "sense" if there is an edge, and if there is, they turn.
		self.sensor_rect_r = pygame.Rect(1, 1, 10, 10)
		self.sensor_rect_l = pygame.Rect(1, 1, 10, 10)

		self.colliding_mats = ["solid", "soft-break", "hard-break", "shot-break", "fire-break"]
		self.state_stack = [None for i in range(5)]

	def update(self, game_actor, engine):
		# Update sensor-rects
		self.sensor_rect_r.topleft = game_actor.rect.bottomright
		self.sensor_rect_l.topright = game_actor.rect.bottomleft

		if self.state == ShStates.MOVE:
			if self.look_direction == LEFT:
				if engine.world.get_colliding_rect(Layers.main, self.colliding_mats, self.sensor_rect_l) is None:
					self.state = ShStates.TURN
			elif self.look_direction == RIGHT:
				if engine.world.get_colliding_rect(Layers.main, self.colliding_mats, self.sensor_rect_r) is None:
					self.state = ShStates.TURN

			if RIGHT in self.colliding_sides or LEFT in self.colliding_sides:
				self.state = ShStates.TURN
			elif not BOTTOM in self.colliding_sides:
				self.state = ShStates.STAY

		elif self.state == ShStates.STAY:
			if BOTTOM in self.colliding_sides:
				self.state = ShStates.MOVE

		self.state_stack.pop(0)
		self.state_stack.append(self.state)

		game_actor.send_message(MSGN.STATE, self.state)
		game_actor.send_message(MSGN.STATESTACK, self.state_stack)
		game_actor.send_message(MSGN.LOOKDIRECTION, self.look_direction)


class LookComponent(StatesComponent):
	def __init__(self):
		super(LookComponent, self).__init__()

		# Initialize all Animation objects:
		self.animations = {}
		walk_r_imgs = split_tiled_image(pygame.image.load(j_path("images", "spearhead", "ANI_walk_r.png")).convert_alpha(), (24, 16))
		self.animations["walk_right"] = Animation(walk_r_imgs, [(2, 15), (0, 15), (1, 15), (0, 15)])
		self.animations["walk_left"] = self.animations["walk_right"].make_x_mirror()

		self.animations["stand_right"] = Animation(walk_r_imgs, [0, 600])
		self.animations["stand_left"] = self.animations["stand_right"].make_x_mirror()

		turn_imgs = split_tiled_image(pygame.image.load(j_path("images", "spearhead", "ANI_turn_l.png")).convert_alpha(), (24, 16))
		self.animations["turn_left"] = Animation(turn_imgs, [(0,8), (1, 4), (0, 8), (1, 4), (0, 15), (1, 2), (0, 8), (2, 8), (3, 8), (4, 8), (5, 30), (5, 1)])
		self.animations["turn_right"] = self.animations["turn_left"].make_x_mirror()

		# Save the current animation
		self.current_animation = self.animations["stand_right"]
		# Save the last animation to check if a new animation has started:
		self.current_animation_name = "stand_right"
		# Play the current animation
		self.current_animation.play()

	def receive_message(self, name, value):
		super(LookComponent, self).receive_message(name, value)

	def update(self, game_actor, engine):
		if self.state == ShStates.MOVE:
			if self.look_direction == RIGHT:
				self.play_animation("walk_right")
			elif self.look_direction == LEFT:
				self.play_animation("walk_left")
		elif self.state == ShStates.STAY:
			if self.look_direction == RIGHT:
				self.play_animation("stand_right")
			elif self.look_direction == LEFT:
				self.play_animation("stand_left")
		elif self.state == ShStates.TURN:
			if self.look_direction == LEFT:
				self.play_animation("turn_right")
			elif self.look_direction == RIGHT:
				self.play_animation("turn_left")

			if self.current_animation.get_spritenr()+1 == self.current_animation.get_animation_length():
				self.state = ShStates.MOVE
				# Turn:
				if self.look_direction == LEFT:
					self.look_direction = RIGHT
					self.play_animation("walk_right")
				else:
					self.look_direction = LEFT
					self.play_animation("walk_left")

		# Update the current animation:
		self.current_animation.update()

		# Calculate the position of the image so its midbottom is aligned with the midbottom of the game_actor
		if self.look_direction == RIGHT:
			surface_pos = self.current_animation.get_surface().get_rect(bottomleft = game_actor.rect.bottomleft)
		else:
			surface_pos = self.current_animation.get_surface().get_rect(bottomright = game_actor.rect.bottomright)

		# Blit the current sprite to the screen:
		engine.graphics.blit(self.current_animation.get_surface(), surface_pos)

		# Update the other components:
		game_actor.send_message(MSGN.STATE, self.state)
		game_actor.send_message(MSGN.LOOKDIRECTION, self.look_direction)

	def play_animation(self, animation_name):
		"""Plays an animation only if the wanted animation isn't
		already playing.
		"""
		if self.current_animation_name != animation_name:
			self.current_animation_name = animation_name
			self.current_animation = self.animations[self.current_animation_name]
			self.current_animation.reset()
			self.current_animation.update()


class MoveComponent(StatesComponent, VelocityComponent):

	def __init__(self):
		super(MoveComponent, self).__init__()
		self.walk_speed = 0.5
		self.velocity = (0, 0)

	def receive_message(self, name, value):
		super(MoveComponent, self).receive_message(name, value)
		if name == MSGN.VELOCITY:
			self.velocity = value

	def update(self, game_actor, engine):
		if self.state == ShStates.MOVE:
			if self.look_direction == LEFT:
				self.velocity = -self.walk_speed, self.velocity[1]
			else:
				self.velocity = self.walk_speed, self.velocity[1]

		elif self.state == ShStates.STAY or self.state == ShStates.TURN:
			self.velocity = 0, self.velocity[1]

		game_actor.send_message(MSGN.VELOCITY, self.velocity)
