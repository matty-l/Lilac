"""

	This class contains classes to be passed to a Module

	Author: Matthew Levine
	Date: 09/04/2014

"""

from abc import ABCMeta, abstractmethod

class ModuleElement(object):
	""" This class can be carried by a Module. It's subclasses include:
		
		- Shape
		- MatrixTransformation
		
	"""
	
	__metaclass__ = ABCMeta
	
	def __init__( self ):
		self.__is_dirty = False
		self.ignore = False
		self.quick = False
		
	def _is_dirty( self ):
		""" This should return true whenever the canvas needs to be redrawn
			due to this element. Individual methods are responsible for setting
			this flag when they feel it is necessary
		"""
		return self.__is_dirty
		
	def _dirty( self ):
		""" Sets the dirty flag to true """
		self.__is_dirty = True
		
	def _clean( self ):
		""" Unsets the dirty flag to false """
		self.__is_dirty = False
		
	@abstractmethod
	def apply_to_scene( self, ltk ):
		""" Draws the module element onto the image using the given Ltk instance.
			If the module element is a shape, this might involve setting
			the pixel values on the image; if it is a matrix transformation,
			this involves applying the correct linalg operation to existing point
			models.
			
			This method must be overwritten by implementing classes
		"""
		return
	
	@abstractmethod
	def accept( self, visitor ): 
		""" Applies the visitor pattern for all module elements """
		return None