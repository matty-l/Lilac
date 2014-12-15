"""
	This file contains a visitor that returns all the objects contained
	by a rectangle.
	
	Author: Matthew Levine
	Date: 10/13/2014
"""

from Module.ClassUtils import Overrides

class ContainmentVisitor(Visitor):

	def get_contained_elements( self, mod, x0, y0, x1, y1 ):
		self.rect = (x0,y0,x1,y1)
		mod.accept(self)
		
	@Overrides(Visitor)
	def visit_module(self, mod):
		