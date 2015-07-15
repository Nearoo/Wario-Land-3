from abc import ABCMeta, abstractmethod


class EngineController(object):
	"""
	Baseclass for Engine-controllers.
	Every engine needs to override a certain part of the engine-wrapper.
	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def __init__(self, engine_wrapper):
		self.engine_wrapper = engine_wrapper
