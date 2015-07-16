from abc import ABCMeta, abstractmethod


class EngineController(object):
	"""
	Baseclass for Engine-controllers.
	Every engine needs to override a certain part of the engine-wrapper.
	:param engine: The complete engine, used to access every other part of it.
	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, engine):
		self.engine = engine
