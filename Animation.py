from globals import pygame


class Animation:
	"""
	The animation class is very useful to handle sprite-animations.
	It is recommended to create a class that inherits from this one and then 
	change the _custom()-method to add custom behaviour.

	Most methods who aren't getters return self in order to perform actions like
	animation.pause().reset().get_surface()

	"""
	def __init__(self, sprites, sprite_order):
		"""
		sprites: A list of images of the sprite, each image is a frame of the animation.
			The images all have to have the same size.
			See utilities.split_tiled_surface() for an easy way to generate such a list.

			Sprites can't have an alpha-channel, transparent parts must be indicated by the
			color (225, 0, 225)

		sprite_order: Can be three of the following things:
			Amount (int) of frames every sprite is showed. The order of the sprites played will be the order of the
			sprites in the "sprites"-argument.

			OR

			The amount of frames for every sprites (list). The order of the sprites played will be the order of the
			sprites in the "sprites"-argument, but this time, the amount of frames each sprite is showed can be changed
			individually. ([frames_for_image_1, frames_for_image_2...])

			OR

			The order of the sprites and the amount of frames for every sprite (list of tuples). This list can contain
			more elements than there are sprites. The syntax for this list is [(sprite_nr, frame_length),
			(sprite_nr, frame_length)...].
			An animation with three different sprites can be 5 sprites long,
			playing sprite |: 1, 2, 1, 3, 2 :| for 100 frames per sprite for instance would be expressed as follows:
			Animation([surface_1, surface_2, surface_3], [(1, 100), (2, 100), (1, 100), (3, 100), (1, 100)])
		"""

		# Save the sprites-list
		self.sprites = sprites

		# Save the speed and order of sprites according to the type of the given list:
		self.sprite_order = sprite_order
		self.format_sprite_order()

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
		Plays the animation, meaning surface and frame-number get updated over time
		"""

		self.playb = True
		return self

	def pause(self):
		"""
		Pauses the animation.
		"""
		self.playb = False
		return self

	def reset(self):
		"""
		Resets the animation to the first frame without pausing it.
		"""
		# Sets the current sprite to 0:
		self.current_sprite = 0
		# Makes the surface empty:
		self.surface.blit(self.empty_surface, (0, 0))
		# Blit the image of the new frame onto the surface
		self.surface.blit(self.sprites[self.sprite_order[self.current_sprite][0]], (0, 0))
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
		self.sprite_order = frames_per_image

		# Make sure self.sprite_order is a list containing the speed for every frame, (convert int to list)
		self.format_sprite_order()

		return self

	def set_colorkey(self, color):
		"""
		Sets the colorkey of all sprites.
		"""
		for sprite in self.sprites:
			sprite.set_colorkey(color)
		return self

	def _custom(self):
		"""
		This function is called at the same time update() is called.
		It is used by classes who inherit from this one to add custom behaviour.
		"""
		pass

	def format_sprite_order(self):
		if type(self.sprite_order) is list:
			if type(self.sprite_order[0]) is tuple:
				# sprite_order is already formatted:
				self.sprite_order = self.sprite_order
			else:
				# sprite_order consists of amounts of frames for sprites:
				self.sprite_order = \
					[(sprite, length) for sprite, length in zip(range(len(self.sprites)), self.sprite_order)]
		else:
			# sprite_order consists of one amount of frames for every sprite:
			self.sprite_order = [(sprite, self.sprite_order) for sprite in range(len(self.sprites))]

	def update(self):
		"""
		This method must be called every frame.
		It updates the entire animation-object.
		"""
		# Execute the custom update method used by inherited classes:
		self._custom()
		# Make sure frames_per_image is a list:
		self.format_sprite_order()
		# If animation is currently playing, increase frame_counter
		if self.playb:
			self.frame_counter += 1

		# If the current frame-number exceeds the speed frames_per_image...
		if self.frame_counter >= self.sprite_order[self.current_sprite][1]:
			# Increase the index of the current sprite
			self.current_sprite += 1
			# If the index of the current frame is higher than the length of sprites available, reset it to 0
			if self.current_sprite >= len(self.sprite_order):
				self.current_sprite = 0
			# Clean up the surface
			self.surface.blit(self.empty_surface, (0, 0))
			# Blit the image of the new frame onto the surface
			self.surface.blit(self.sprites[self.sprite_order[self.current_sprite][0]], (0, 0))
			# Reset the frame_counter
			self.frame_counter = 0
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
		Useful for e.g. walk- or jump-animations.
		"""
		new_sprites = [pygame.transform.flip(surf, 1, 0) for surf in self.sprites]
		return self.copy(new_sprites, self.sprite_order)

	def make_y_mirror(self):
		"""
		Mirrors every image of the animation on the y axis.
		Useful for e.g. walk- or jump-animations.
		"""
		new_sprites = [pygame.transform.flip(surf, 0, 1) for surf in self.sprites]
		return self.copy(new_sprites, self.sprite_order)

	def make_xy_mirror(self):
		"""
		Mirrors every image of the animation on the x- and the y-axis.
		Useful for e.g. walk- or jump-animations.
		"""

		new_sprites = [pygame.transform.flip(surf, 1, 1) for surf in self.sprites]
		return self.copy(new_sprites, self.sprite_order)