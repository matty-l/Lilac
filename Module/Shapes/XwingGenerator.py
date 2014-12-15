
from Module.Module import Module
from Module.ClassUtils import Overrides
from Module.Shapes.Polygon import Polygon
from Module.Shapes.ObjGenerator import ObjGenerator
from Module.Lighting.Colors import Colors
from numpy import array as nparray
from math import sin,cos,pi

body_width=2

class XwingGenerator(ObjGenerator):

	def __init__( self, shape_factory ):
		""" Initializes the xwing generator """
		ObjGenerator.__init__(self)
		global ShapeFactory
		ShapeFactory = shape_factory # good code is good
		self.build_mesh()
		
	@Overrides(ObjGenerator)
	def build_mesh(self):
		""" Builds the xwing mesh """
		cylinder = lambda sides : ShapeFactory().gen_shape('cylinder')
		box = lambda : ShapeFactory().gen_shape('box')
		
		# engine
		engine = Module()
		engine.scale( 1.3, 6, 1.3 )
		engine.rotate( 0, 1, 'x' )
		engine.add_element( cylinder(sides=10) )
		engine.scale(.8,.8,1.1)
		engine.body_color(Colors.FLAME)
		# engine.body_color(Colors.WHITE)
		engine.add_element( cylinder(sides=10) )
		
		# laser
		laser = Module()
		laser.scale(.5,5,.5)
		laser.rotate(0,1,'x')
		laser.add_element( cylinder(sides=6) )
		laser.scale(0.4,0.4,1)
		laser.translate(0,0,4.5)
		laser.body_color(Colors.OFF_RED)
		# laser.body_color(Colors.WHITE)
		laser.add_element( cylinder(sides=10) )
		
		# wing
		wing = Module()
		poly = Polygon( nparray( [[0,0,0,1],[0,0,5,1],[15,0,3,1],[15,0,0,1]] ),
			normals=nparray([[0,-1,0,1]for i in range(4)]))
		wing.add_shape( poly )
		wing.translate(0,.5,0)
		Polygon( nparray( [[0,0,0,1],[0,0,5,1],[15,0,3,1],[15,0,0,1]] ),
			normals=nparray([[0,1,0,1]for i in range(4)]))
		wing.add_shape( poly )
		wing.identity()
		wing.translate( 3, 1.6, -1 )
		wing.add_element( engine )
		wing.identity()
		
		poly = Polygon( nparray( [[15,0,3,1],[15,0,0,1],[15,.5,0,1],[15,.5,3,1]] ),
			normals= nparray([[1,0,0,1]for i in range(4)]))
		wing.add_shape( poly )
		poly = Polygon( nparray( [[15,0,0,1],[0,0,0,1],[0,.5,0,1],[15,.5,0,1]] ),
			normals= nparray([[0,0,-1,1]for i in range(4)]))
		wing.add_shape( poly )
		poly = Polygon( nparray( [[15,0,3,1],[15,0.5,3,1],[0,.5,5,1],[0,0,5,1]] ),
			normals= nparray([[2,0,15,1]for i in range(4)]))
		wing.add_shape( poly )
		
		wing.translate( 15, .25, 0 )
		wing.add_element( laser )
		
		# 4 Wings
		wings = Module()
		wings.body_color( Colors.GREY )
		# wings.body_color(Colors.WHITE)
		wings.rotate( cos(.3),sin(.3), 'z' )
		wings.translate( body_width, 0, 0 )
		wings.add_element(wing)
		
		wings.identity()
		wings.scale(1,-1,1)
		wings.rotate(cos(-.3),sin(-.3),'z')
		wings.translate(body_width,0,0)
		wings.add_element(wing)
		
		wings.identity()
		wings.scale(-1,1,1)
		wings.rotate(cos(-.3),sin(-.3),'z')
		wings.translate(-body_width,0,0)
		wings.add_element(wing)
		
		wings.identity()
		wings.scale(-1,-1,1)
		wings.rotate(cos(.3),sin(.3),'z')
		wings.translate(-body_width,0,0)
		wings.add_element(wing)
		
		# body
		body = Module()
		body.surface_color(Colors.DARK)
		body.body_color(Colors.GRAY)
		# body.body_color(Colors.FLAME)
		# body.body_color(Colors.WHITE)
		body.add_element(wings)
		body.scale(body_width,body_width,8)
		body.translate(0,0,4)
		body.add_element( box() )
		
		body.identity()
		# body.body_color(Colors.FLAME)
		body.body_color(Colors.GRAY)
		poly = Polygon( nparray([
			[body_width,body_width,12,1],
			[body_width,-body_width,12,1],
			[body_width*.5,-body_width*.3,35,1],
			[body_width*.5,body_width*.3,35,1]]),
			normals= nparray([[23,0,.5*body_width,1]for i in range(4)]))
		body.add_shape( poly )
		
		poly = Polygon( nparray([
			[-body_width,body_width,12,1],
			[-body_width,-body_width,12,1],
			[-body_width*.5,-body_width*.3,35,1],
			[-body_width*.5,body_width*.3,35,1]]),
			normals= nparray([[-23,0,.5*body_width,1]for i in range(4)]))
		body.add_shape(poly)
		
		poly = Polygon( nparray([
			[-body_width,body_width,12,1],
			[body_width,body_width,12,1],
			[body_width*.5,body_width*.3,35,1],
			[-body_width*.5,body_width*.3,35,1]]),
			normals= nparray([[0,23,.5*body_width,1]for i in range(4)]))
		body.add_shape(poly)
			
		poly = Polygon( nparray([
			[-body_width,-body_width,12,1],
			[body_width,-body_width,12,1],
			[body_width*.5,-body_width*.3,35,1],
			[-body_width*.5,-body_width*.3,35,1]]),
			normals= nparray([[0,-23,.5*body_width,1]for i in range(4)]))
		body.add_shape(poly)
		
		poly = Polygon( nparray([
			[-body_width*.5, body_width*.3,35,1],
			[ body_width*.5, body_width*.3,35,1],
			[ body_width*.5,-body_width*.3,35,1],
			[-body_width*.5,-body_width*.3,35,1]]),
			normals= nparray([[0,0,1,1]for i in range(4)]))
		body.add_shape(poly)

		body.id[0] = 'Xwing'
		self.mesh = body