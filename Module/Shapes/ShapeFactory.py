"""
	This class applies the factory pattern to shapes and applies
	dependency injection to ensure that the factory is used once
	without falling back on the singleton pattern. For this reason,
	this file can only be imported once per program execution.
	
	Author: Matthew Levine
	Date: 09/04/2014
"""

# Import all the shapes
from Module.Shapes.Point import Point
from Module.Shapes.PointCloud import PointCloud
from Module.Shapes.Line import Line
from Module.Shapes.PolyLine import PolyLine
from Module.Shapes.Polygon import Polygon
from Module.Shapes.SphereGenerator import SphereGenerator
from Module.Shapes.XwingGenerator import XwingGenerator

from Module.Module import Module
from math import cos, sin, pi
from Module.Lighting.Colors import Colors

from numpy import array as nparray	
	
from random import randint as ra

from Module.Shapes.CastleU  import genCurve
	
class ShapeFactory:
	""" This class applies the factory pattern to shapes
	"""
	
	__cache__ = {}
	cache = True
	sphere = None
	
	
	def gen_shape( self, id, **opts ):
		""" Returns a point object """
		if not id in self.__shape_name_map:
			raise ShapeImposterException("Unrecognised shape: "+str(id))
		if self.cache and not str(id) in self.__cache__:
			self.__cache__[str(id)] = self.__shape_name_map[ id ]( **opts )
		return (self.__cache__[str(id)] if self.cache else link( self.__shape_name_map[ id ]( **opts )).average_normals() )

	def __create_rectangle( width=.1, height=.1, x0=0, y0=0, color =[0,0,0,0] ):
		""" Returns a rectangle shape.
			
			The class of the square will be "Polygon", and will be treated
			as a polygon generated through manual polygon construction.
		"""
			
		vertices = nparray([ [-width+x0,-height+y0,0,1], [-width+x0,height+y0,0,1],
			[width+x0,height+y0,0,1], [width+x0,-height+y0,0,1] ] )
		colors = nparray([255,0,0,0])	
		return Polygon( vertices, color = color )
		
	def __create_box( width=1, height=1, depth=1, x0=0, y0=0, z0=0,
			color = [[200,200,0,0] for i in range(6)] ):
		""" Returns a box shape.
			
			The class of the square will be "Module", and will be treated
			as a module generated through manual module construction.
		"""
		box = Module()
		(w,h,d) = (width,height,depth) # for conciseness
		
		# Back
		vertices = nparray([ [-w+x0,-h+y0,-d+z0,1],[-w+x0,h+y0,z0-d,1],[w+x0,h+y0,z0-d,1],
			[w+x0,-h+y0,z0-d,1] ] )
		box.add_shape( Polygon(vertices, color = color[0], normals=nparray([0,0,-1,0]),
			anchor=nparray([[0,255,-1,-1], [0,0,-1,-1], [255,0,-1,-1], [255,255,-1,-1]]).flatten().astype(int)) ) 
		
		# Front
		vertices = nparray([ [-w+x0,-h+y0,d+z0,1],[-w+x0,h+y0,z0+d,1],[w+x0,h+y0,z0+d,1],
			[w+x0,-h+y0,z0+d,1] ] )
		box.add_shape(Polygon( vertices, color = color[1], normals=nparray([0,0,1,0]),
			anchor=nparray([[0,255,-1,-1], [0,0,-1,-1], [255,0,-1,-1], [255,255,-1,-1]]).flatten().astype(int)) ) 

		
		# Left
		vertices = nparray([ [-w+x0,-h+y0,d+z0,1], 
			[-w+x0,-h+y0,z0-d,1], [-w+x0,h+y0,z0-d,1], [-w+x0,h+y0,z0+d,1] ] )
		box.add_shape( Polygon( vertices, color = color[2],normals=nparray([-1,0,0,0]),
			anchor=nparray([[0,0,-1,-1], [255,0,-1,-1], [255,255,-1,-1], [0,255,-1,-1]]).flatten().astype(int)) ) 
		
		# Right
		vertices = nparray([ [w+x0,-h+y0,d+z0,1], [w+x0,-h+y0,z0-d,1], [w+x0,h+y0,z0-d,1], 
			[w+x0,h+y0,z0+d,1] ] )
		box.add_shape( Polygon( vertices, color = color[3],normals=nparray([1,0,0,0]),
			anchor=nparray([[0,0,-1,-1], [255,0,-1,-1], [255,255,-1,-1], [0,255,-1,-1]]).flatten().astype(int)) )
		
		# Top
		vertices = nparray([ [-w+x0,h+y0,d+z0,1], [-w+x0,h+y0,z0-d,1], [w+x0,h+y0,z0-d,1],
			[w+x0,h+y0,z0+d,1] ] )
		box.add_shape( Polygon( vertices, color = color[4],normals=nparray([0,1,0,0]),
			anchor=nparray([ [0,0,-1,-1],[0,255,-1,-1], [255,255,-1,-1], [255,0,-1,-1]]).flatten().astype(int)) )
		
		# Bottom
		vertices = nparray([ [-w+x0,-h+y0,d+z0,1],[-w+x0,-h+y0,z0-d,1],[w+x0,-h+y0,z0-d,1],
			[w+x0,-h+y0,z0+d,1] ] )
		box.add_shape( Polygon( vertices, color = color[5],normals=nparray([0,-1,0,0]),
			anchor=nparray([ [0,0,-1,-1],[0,255,-1,-1], [255,255,-1,-1], [255,0,-1,-1]]).flatten().astype(int)) )
		box.id[0] = 'Box'
		return box
		
	def __create_bezier():
		
		curve = Module()
		points = normals = genCurve()
		curve.add_shape(Polygon(points,normals=points))
		return curve


	def __create_cylinder( width=1, height=1, sides=50, x0=0, y0=0, z0=0,
			color = [0,0,200,0] ):
		""" Returns a cylinder shape.
			
			The class of the cylinder will be "Module", and will be treated
			as a module generated through manual module construction.
		"""
		cylinder = Module()
		
		mx = 255 // sides
				
		for i in range(sides):
			part1 = i * pi * 2 / sides
			part2 = (i+1)%sides * pi * 2 / sides
			x1 = cos(part1) * width
			z1 = sin(part1) * height
			x2 = cos(part2) * width
			z2 = sin(part2) * height
			x1a = cos(part1) * 120 + 120
			z1a = sin(part1) * 120 + 120
			x2a = cos(part2) * 120 + 120
			z2a = sin(part2) * 120 + 120			
			
			cylinder.add_shape(Polygon(nparray([ [x1,1,z1,1], [x2,1,z2,1],
				[0,1,0,1] ] ),color=color,normals=nparray([[0,1,0,1]for i in range(4)]),
				anchor=nparray([[0,i*mx,-1,-1],[0,(i+1)*mx,-1,-1],
				[255,i*mx,-1,-1],[255,(i+1)*255,-1,-1]]).flatten().astype(int))) 
					
			cylinder.add_shape(Polygon(nparray([ [x1,0,z1,1], [x2,0,z2,1],
				[0,0,0,1]] ),color=color,normals=nparray([[0,-1,0,1]for i in range(4)]),
				anchor=nparray([[0,i*mx,-1,-1],[0,(i+1)*mx,-1,-1],
				[255,i*mx,-1,-1],[255,(i+1)*255,-1,-1]]).flatten().astype(int))) 

			cylinder.add_shape( Polygon(nparray(\
			[	[x1,0,z1,1], [x2,0,z2,1], [x2,1,z2,1], [x1,1,z1,1]  ] ),
			color=color,normals=nparray([[x1,0,z1,1],[x2,0,z1,1],[x2,0,z1,1],[x1,0,z1,1]]),
				anchor=nparray([[i*mx,0,-1,-1],[(i+1)*mx,0,-1,-1],
				[i*mx,255,-1,-1],[(i+1)*mx,255,-1,-1]]).flatten().astype(int))) 
		
		cylinder.id[0] = 'Cylinder'
		return cylinder
		
	def __create_xwing( x0=0,y0=0,z0=0,body_width = 2 ):
		""" Returns an xwing shape
			
			The class of the xwing will be "Module"
			Take from Bruce Maxwell's Xwing code "test8b.c"
		"""
		s = XwingGenerator(ShapeFactory).mesh
		s.id[0] = 'Xwing'
		return s
		
	def __create_sphere(resolution=2):
		""" Returns a sphere object.
			
			The argument resolution specifies the number of recursions to apply
			when generating the sphere; note that because complex shapes are cached
			for performance, this can only be applied to the first sphere
			unless the cache is manually cleared.
		"""
		s = SphereGenerator(recursion=resolution).mesh
		s.id[0] = 'Sphere'
		return s 
		
		
		
		
	def module_names( self ):
		""" Returns a generator of the possible module names """
		return ('box','sphere','cylinder','teapot','xwing')
		
		# return ('box','xwing','sphere','cylinder','man','walrus','tank','tree',
			# 'grass','hill','piano','castle','knight','dragon','teapot','wine glass','chess')
			
	__shape_name_map = { 'point' : Point, 'pointcloud' : PointCloud,
						 'line' : Line, 'polyline': PolyLine,
						 'polygon' : Polygon, 'rectangle' : __create_rectangle,
						 'box' : __create_box, 'cylinder': __create_cylinder,
						 'xwing' : __create_xwing, 'sphere': __create_sphere,
						 # These are examples of other objects which have been
						 # build for this project
						 # 'man' : __create_man, 'apple': __create_apple,
						 # 'cup':__create_tank, 'tree':__create_tree1,
						 # 'grass':__create_grass,'hill':__create_hill,
						 # 'pear':__create_pear,'castle':__create_castle,
						 # 'knight':__create_knight, 'dragon':__create_dragon,
						 # 'teapot':__create_teapot,'wine glass':__create_glass,
						 # 'curve':__create_bezier,'meteor':__create_meteor,
						 
						 # 'rook':__create_rook,'knight':__create_knight,
						 # 'bishop':__create_bishop,'king':__create_king,'queen':__create_queen,'pawn':__create_pawn,
						}

class ShapeImposterException(Exception): pass

def link( shape ):
	try: shape.__elements__[-1].__elements__[0] = shape.__elements__[0]
	except: pass
	return shape
						
if __name__ != '__main__':
	import sys
	sys.modules['ShapeFactory'] = None
	shape_factory = ShapeFactory()
		
else:
	raise Exception("The Shape Factory has no primary executable functions")