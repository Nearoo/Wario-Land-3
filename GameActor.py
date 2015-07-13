import pygame

class GameActor(object):
	def __init__(self, position, Input, World, Graphics):
		# Save pointers to the important classes
		self.input = Input
		self.world = World
		self.graphics = Graphics
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
			component.update(self)

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