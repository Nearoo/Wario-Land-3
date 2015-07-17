from Actors import *
import logging
from EngineController import *


class GameActorController(EngineController):
	"""
	Cares for and contains all game-actors active or inactive in the game.
	"""

	def __init__(self, engine, log_level = logging.ERROR):
		super(GameActorController, self).__init__(engine)
		# All game-actors, sorted by instance id (id())
		self.actors = {}
		# Create deletion buffer-list, so actors can't delete while updating:
		self.actor_deletion_list = []
		self.current_game_actor = None

		self.game_actor_types = {"Wario": Wario, "Spearhead": SpearHead}

		# Create logger
		self.logger = logging.getLogger("Game Actor Controller")
		self.logger.setLevel(log_level)

	def _check_actor_id(self, actor_id):
		"""
		Makes an actor-id out of a given object if it isn't already one and checks if
		the id corresponds to an existing game-actor. If not, an exeption is raised.
		:param actor_id: The object of which the id should be checked
		:return: The id.
		"""

		# If actor_id isn't an id, make it the id of what it is, else leave it
		actor_id = id(actor_id) if type(actor_id) != int else actor_id
		# Make sure the id is existent:
		assert actor_id in self.actors, "Non-existent GameActor with id %i" % actor_id
		return actor_id

	def spawn_game_actor(self, actor_type, position, input, world, graphics, sound):
		"""
		Spawns a new game-actor and adds it to its own list.
		:param actor_type: The type of the new game-actor, e.g. "Wario"
		:param position: The position of the new game-actor
		:param input: The input-engine
		:param world: The world-controller
		:param graphics: The graphics-controller
		:param sound: The sound-controller
		:return: None
		"""
		# Check if game_actor_type is existent:
		assert actor_type in self.game_actor_types, "Unknown GameActor-type \"%s\""
		# Create new actor:
		new_actor = self.game_actor_types[actor_type](position, self.engine)
		# Add it to list
		self.actors[id(new_actor)] = new_actor

		# Log the event:
		self.logger.debug("Created game-actor with type %s at position (%f, %f) with %i" %
			(actor_type, position[0], position[1], id(new_actor), ))

	def kill_game_actor(self, actor_id):
		"""
		Kills a game-actor the next time update() is called.
		:param actor_id: The id of the actor that should be killed.
		:return: None
		"""
		actor_id = self._check_actor_id(actor_id)
		# Append it to the deletion_list:
		if actor_id not in self.actor_deletion_list:
			self.actor_deletion_list.append(actor_id)

	def update(self):
		# Update the game-actors
		for actor in self.actors.items():
			self.current_game_actor = actor[0]
			actor[1].update()

		# Delete the wanted game-actors:
		for actor_id in self.actor_deletion_list:
			del self.actors[actor_id]
			self.logger.debug("Deleted game-actor with id {0}.".format(actor_id))

	def send_actor_message(self, sender_id, receiver_id, name, value):
		"""
		Sends a message to another actor in the game, e.g. "damage"
		:param sender_id: The id of the game-actor who sent the message.
		:param receiver_id: The id of the game-actor to whom the message should be sent to.
		:param name: The name of the message, e.g. "damage".
		:param value: The value of the message, e.g. 10.
		:return: None.
		"""
		receiver_id = self._check_actor_id(self, receiver_id)

		self.actors[receiver_id].send_actor_message(sender_id, name, value)

	def get_colliding_actors(self, actor_id):
		"""
		Checks for collision of one game-actor with all other game-actors.
		:param actor_id: Can be a game-actor or a game-actor-id
		:return: A list containing all game-actors that collide.
		"""
		current_actor_id = self._check_actor_id(actor_id)
		tmp_rects = {actor[0]: actor[1].rect for actor in self.actors}
		del tmp_rects[current_actor_id]
		return [self.actors[actor_rect[0]] for actor_rect in
				self.actors[current_actor_id].rect.collidedictall(tmp_rects)]
