from globals import pygame


class EngineWrapper:
	"""Only exists to make it impossible for the components
	to access things of the engine they shouldn't. It only contains
	the instances of important things like input, world, or graphics."""
	input = None
	world = None
	graphics = None
	sound = None
	actors = None

	def __init__(self, input, world, graphics, sound=None, actors = None):
		self.input = input
		self.world = world
		self.graphics = graphics
		self.sound = sound
		self.actors = actors


class GameActor(object):
	def __init__(self, position, input, world, graphics, sound, actors):
		# Update the static variable engine:
		# This is kind of dangerous if we had multiple engines. Luckily we don't.
		self.engine = EngineWrapper(input, world, graphics)
		# Create to own rect
		self.rect = pygame.Rect(position, (1, 1))
		# Initialize the var used later (see self.update & self.send_message)
		self.current_component = None
		# Initialize the components list, classes inheriting from this one will fill it with components
		self.components = []

	def update(self):
		"""Updates every component - should not be changed by inheriting classes!"""
		# For every component
		for component in self.components:
			# Save to current component so components don't send messages to themselves (see self.send_message())
			self.current_component = component
			# Update the compontent, handig over input, world and graphics
			component.update(self, self.engine)

		# Call the private update-method - used by inhertiting classes.
		self._update()

	def _update(self):
		"""This method should be changed by inheriting classes, using the data the components have manipulated"""
		pass

	def send_message(self, name, value):
		"""
		Used by the components to send messages to all other components.
		Weather the other components do something with it is up to themselves.
		"""
		# For everycomponent
		for component in self.components:
			# ...except the one that is sending the message (see self.update())
			if component is not self.current_component:
				# Sen the message
				component.receive_message(name, value)

	def receive_actor_message(self, sender_id, name, value):
		"""
		Used by other GameActors to send messages like "damage" to this instance.
		:param name: The name of the message, e.g. "damage"
		:param value: The value of the message, e.g. 10
		:return: None
		"""
		pass