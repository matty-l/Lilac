"""
	This file contains a class that updates spheres to a higher
	resolution.
	
	Author: Matthew Levine
	Date: 09/20/2014

"""

# texture = ['earth.tif']*1000 #, 'jupiter.jpg','pluto.jpg'] * 1000
# texture = ['earth.jpg','moon.jpg'] * 1000
texture = ['earth.jpg','jupiter.jpg','mars.jpg', 'pluto.jpg'] * 1000

from Module.Visitors.Visitor import Visitor
from Module.ClassUtils import Overrides
from Module.Shapes.SphereGenerator import SphereGenerator

typecheck = lambda obj1, obj2 : isinstance(obj1,Polygon) # not OO cool but ok
islist = lambda obj1 : isinstance(obj1,list) # not OO cool but ok

class SphereUpdateVisitor(Visitor):
	""" This class uses double dispatch to gather display information
		for tables
	"""
	
	def update_spheres( self, root ):		
		SphereGenerator.__cache__ = None
		# self.texture = texture[:]
		self.mesh = SphereGenerator(recursion=8).mesh
		root.accept( self )
		root._dirty()			
		
		
	
	@Overrides(Visitor)
	def visit_module( self, module ):
		""" Descends down a module looking for spheres """
		function = self.mesh.apply_to_scene
		for i,element in enumerate(module.__elements__):
			if islist(element.id) and element.id[0] == 'Sphere':
				module.__elements__[i].__elements__[-1] = self.mesh	
				# decorate the sphere's draw method to also texture the sphere
				def application_decorator( function, mesh, textures ):
					def inner(environment):
						text = texture.pop(0)
						SphereGenerator.texture_sphere( mesh, text )
						function(environment)
					return inner
					
				# self.mesh.apply_to_scene = application_decorator(function,self.mesh,texture)			
			else:
				element.accept(self)
