"""
	This file contains a class that toggles visible and invisible modules
	
	Author: Matthew Levine
	Date: 10/22/2014

"""


from Module.Visitors.Visitor import Visitor
from Module.ClassUtils import Overrides

class FlipVisitor(Visitor):
	
	def flip_all( self, root ):		
		for element in root.__elements__: # don't accept the root
			element.accept(self)
	
	@Overrides(Visitor)
	def visit_module( self, module ):
		module.ignore = not module.ignore
