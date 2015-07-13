from Animation import *
from utilities import *

from pygame.locals import *
from globals import pygame

from locals import *


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
		if name == VELOCITY:
			self.velocity = list(value)


class StatesComponent(GameActorComponent):
	def __init__(self):
		self.colliding_sides = []
		self.state = "standing"
		self.look_direction = "right"

	def receive_message(self, name, value):
		if name == WARIO_STATE:
			self.state = value
		elif name == WARIO_LOOKDIRECTION:
			self.look_direction = value
		elif name == COLLISION_SIDES:
			self.colliding_sides = value
