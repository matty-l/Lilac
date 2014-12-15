from Module.Visitors.Visitor import Visitor
from Module.ClassUtils import Overrides
from math import sin,cos,pi
from random import random

class ExplosionVisitor(Visitor):

	def explode( self, mod, precision, depth_control = 1, radius = 1 ):
		self.i = 1
		self.NE = precision
		self.D = depth_control
		self.r = radius
		mod.accept(self)
	
	@Overrides(Visitor)
	def visit_module( self, mod ):
		for el in mod.__elements__: el.accept(self)
		
	@Overrides(Visitor)
	def visit_polygon( self, poly ):
		x = 2 * pi * self.i / self.NE
		cosx,sinx = cos(x), sin(x)
		d = self.D
		r = self.r
		for side in poly.coordinates:
			side += [(cosx*sinx+.1)/r,(sinx*sinx+.1)/r,cosx/r,0]
		self.i += 1
