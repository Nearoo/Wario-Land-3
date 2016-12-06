from .locals import *

from Animation import *
from utilities import *

from globals import pygame
from pygame.locals import *


class GameActorComponent(object):
	"""
	GameActorComponents are components used by the superclass game-actor.
	They always and only perform one single task, for instance draw the sprite relative to the movement,
	or move relative to the keys pressed by the user.

	Everything they need they store themselves - if they need to communicate with each other, they can either
	send a message using game_actor.send((name, value)) or receive a message using self.recieve_message(message)."""

	def update(self, game_actor, engine):
		"""
		Args:
			engine: The engine singleton. Use to interact with the engine (e.g. engine.graphics, engine.world etc..)
			game_actor: The game actor this component is supposed to change
		"""
		pass

	def receive_message(self, name, value):
		"""Recieve a message (a touple: (name, value)) from other components."""
		pass


class VelocityComponent(GameActorComponent):
	"""
	Can be used for inheritance for components that only listen to the message "velocity".
	"""
	def __init__(self):
		self.velocity = [0, 0]

	def receive_message(self, name, value):
		if name == MSGN.VELOCITY:
			self.velocity = list(value)


class StatesComponent(GameActorComponent):
	def __init__(self):
		self.colliding_sides = []
		self.state = WarioStates.UPRIGHT_STAY
		self.look_direction = RIGHT

	def receive_message(self, name, value):
		if name == MSGN.STATE:
			self.state = value
		elif name == MSGN.LOOKDIRECTION:
			self.look_direction = value
		elif name == MSGN.COLLISION_SIDES:
			self.colliding_sides = value
