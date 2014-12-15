"""
	This file contains the abstract Shape class.
	
	The class uses the factory pattern to produce sub-shapes 
	
	Author: Matthew Levine
	Date: 09/04/2014
"""

from abc import ABCMeta, abstractmethod
from Module.ModuleElement import ModuleElement
from numpy import newaxis
from Module.ClassUtils import Overrides

class Shape(ModuleElement):
	""" This is the parent of all shapes drawn in Lilac.c """
	
	__metaclass__ = ABCMeta
	__id__ = 0
	
	@Overrides(ModuleElement)
	@abstractmethod
	def apply_to_scene( self, shape ):
		""" Draws the shape. This should be overwritten as needed - if drawing
			the objects implicates a redraw of the canvas. Not all module
			elements must have this quality.
		"""
		return
		
	def __init__( self ):
		""" Creates a new Shape. Must be called first in constructor. """
		ModuleElement.__init__(self)
		self.coordinates = None
		self._dirty()
		self.id = self.__id__
		Shape.__id__ += 1
		
	def __repr__( self ):
		""" Returns a useful string representation of the Shape """
		return "<"+str(self.__class__)+" : "+str(self.coordinates)+">"
		
	@abstractmethod
	def copy( self ):
		""" Returns a deep copy of the shape.
			
			This should be overwritten by implementing classes.
		"""
		return
		
	def clip (self, width, height ):
		""" Returns true if all of the coordinates are out of bounds """

		truth = all([ coord[0] > width or coord[0] < 0 or coord[1] > height or \
			coord[1] < 0 for coord in self.coordinates ])
		return truth
		
	def homoginize( self ):
		""" Divides each coordinate by its homogenous component """
		self.coordinates[:,0] /= self.coordinates[:,3]
		self.coordinates[:,1] /= self.coordinates[:,3]
		self.coordinates[:,2] *= -1
			
class ShapeImposterException(Exception):
	""" Raised when something extends shape without meeting preconditions """
	pass
	
class __NullShape:
	""" This Shape follows the Null Object pattern """
	def draw_to_image( self, ltk ):
		pass
		
	def __repr__( self ):
		return "<Null Shape>"
		
NULL_SHAPE = __NullShape()