import copy
from globals import pygame

class Animation:
	"""
	The animation class is very usefull to handle sprite-animations.
	It is recommended to create a class that inherits from this one and then 
	change the _costom()-method to add costom behaviour.

	Most methods who aren't getters return self in order to perform actions like
	animation.pause().reset().get_surface()

	"""
	def __init__(self, sprites, frames_per_image):
		"""
		sprites: A list of images of the sprite, each image is a frame of the animation.
			The images all have to have the same size.
			See utilities.split_tiled_surface() for an easy way to generate such a list.

			Sprites can't have an alpha-channel, transparents parts must be indicated by the
			color (225, 0, 225)

		frame_per_image: Determines the general speed of the animaion.
			The number is the frame each image is show on screen, so frame-rate is
			1/frames_per_image - and int.

			OR

			A list with the speed of each frame. ([frame_for_image_1, frame_for_image_2...])
			Both work.
		"""

		# Save the sprites-list
		self.sprites = sprites

		# Save the animation-speed:
		self.frames_per_image = frames_per_image

		# Make sure self.frames_per_image is a list containg the speed for every frame, (convert int to list)
		self.convert_frames_per_image_to_list()

		# Initialize the frame_counter
		self.frame_counter = 0

		# Initialize the var holding the index of the current sprite
		self.current_sprite = 0

		# Create the surface the current frame will be blitted on
		self.surface = pygame.Surface(self.sprites[0].get_size())

		# Set the colorkey (225, 0, 255)
		self.surface.set_colorkey((255, 0, 255))

		# Blit the image of the current frame onto the surface
		self.surface.blit(self.sprites[0], (0, 0))
		
		# Create an empty surface to clean the main surface up after updating
		self.empty_surface = pygame.Surface(self.sprites[0].get_size())
		self.empty_surface.fill((225, 0, 225))

		# Pause the animation
		self.playb = True

		# Create the reference to the own animation
		self.copy = Animation

	def play(self):
		"""
		Plays the animation, meaning suface and frame-number get updated over time
		"""

		self.playb = True
		return self

	def pause(self):
		"""
		Pauses the animation.
		"""
		self.pause
		return self

	def reset(self):
		"""
		Resets the animation to the first frame without pausing it.
		"""
		self.current_sprite = 0
		return self

	def set_spritenr(self, nr):
		"""
		With this function, the current frame can be changed manually.
		"""
		self.current_sprite = nr
		return self

	def set_frames_per_image(self, frames_per_image):
		"""
		With this function, the speed of the animation can be changed.
		The speed is frames per image, so the framerate is 1/speed.
		"""
		# Update the animation-speed:
		self.frames_per_image = frames_per_image

		# Make sure self.frames_per_image is a list containg the speed for every frame, (convert int to list)
		self.convert_frames_per_image_to_list()

		return self

	def set_colorkey(self, color):
		"""
		Sets the colorkey of all sprites.
		"""
		for sprite in self.sprites:
			sprite.set_colorkey(color)
		return self

	def _costom(self):
		"""
		This function is called at the same time update() is called.
		It is used by classes who inherit from this one to add custom behaviour.
		"""
		pass

	def convert_frames_per_image_to_list(self):
		"""Converts a single int that represents the frames_per_image for every frame
		to a list with the same length as self.sprites containing only this value.

		Used to make it easier to create a simple animation. Instead of Animation(sprites, [100, 100, 100, ....])
		only Animation(sprites, 100) is needed.
		"""

		if type(self.frames_per_image) == int:
			self.frames_per_image = [self.frames_per_image for sprite in self.sprites]

	def update(self):
		"""
		This method must be called every frame.
		It updates the entre animation-object.
		"""
		# Execute the costom update method used by inherited classes:
		self._costom()
		# Make sure frames_per_image is a list:
		self.convert_frames_per_image_to_list()
		# If animation is currently playing, increase frame_counter
		if self.playb:
			self.frame_counter += 1

		# If the current frame-number exceeds the speed frames_per_image...
		if self.frame_counter >= self.frames_per_image[self.current_sprite]:
			# Clean up the surface
			self.surface.blit(self.empty_surface, (0, 0))
			# Blit the image of the new frame onto the surface
			self.surface.blit(self.sprites[self.current_sprite], (0, 0))
			# Reset the frame_counter
			self.frame_counter = 0

			# Increase the index of the current frame for the next update
			self.current_sprite += 1
			# If the index of the current frame is higher than the lenght of sprites aviable, reset it to 0
			if self.current_sprite >= len(self.sprites):
				self.current_sprite = 0
		return self

	def get_spritenr(self):
		"""
		Returns the index of the current sprite displayed.
		"""
		return self.current_sprite 	

	def get_surface(self):
		"""
		Returns the current surface.
		"""
		return self.surface

	def make_x_mirror(self):
		"""
		Mirrors every image of the animation on the x axis.
		Usefull for e.g. walk- or jump-animations.
		"""
		new_sprites = [pygame.transform.flip(surf, 1, 0) for surf in self.sprites]
		return self.copy(new_sprites, self.frames_per_image)

	def make_y_mirror(self):
		"""
		Mirrors every image of the animation on the y axis.
		Usefull for e.g. walk- or jump-animations.
		"""
		new_sprites = [pygame.transform.flip(surf, 0, 1) for surf in self.sprites]
		return self.copy(new_sprites, self.frames_per_image)
	def make_xy_mirror(self):
		"""
		Mirrors every image of the animation on the x- and the y-axis.
		Usefull for e.g. walk- or jump-animations.
		"""

		new_sprites = [pygame.transform.flip(surf, 1, 1) for surf in self.sprites]
		return self.copy(new_sprites, self.frames_per_image)