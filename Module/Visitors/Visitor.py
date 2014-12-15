"""
	
	Abstract visitor class.
	
	Author: Matthew Levine
	Date: 09/20/2014
"""
from abc import ABCMeta

class Visitor(object):

	__metaclass__ = ABCMeta

	def visit_module( self, module ):
		for element in module.__elements__:
			element.accept(this)
	
	def visit_polygon( self, polygon ): 
		""" Visits a polygon """
		return None
	
	def visit_matrix( self, matrix ): 
		""" Visits a matrix modifier """
		return None
	
	def visit_drawstate( self, ds ): 
		""" visits a drawstate modifier """
		return None
	
	# less specific than visit polygon
	def visit_shape( self, shape) : 
		""" Visitis a generic shape, less specific than polygon """
		return None