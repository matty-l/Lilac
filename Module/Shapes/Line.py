"""
	This file contains a Line class
	
	Author: Matthew Levine
	Date: 09/04/2014
"""

import numpy as np
from Module.Shapes.Shape import Shape
import Lilac

class Line(Shape):
	""" This class defines a line in space """
	 
	def __init__( self, coords = np.array([[0,0,0],[0,0,0]]),
						color = np.array([0,0,0,0]), pad = True  ):
		""" Initializes the line """
		Shape.__init__(self)
		if pad:
			self.coordinates = np.pad(coords,((0,0),(0,1)),'constant',constant_values=1)
		else: self.coordinates = coords
		self.color = color

		if self.coordinates.shape != (2,4) or color.shape != (4,):
			s = "Color data must be in rgba form; line shape must be 2 x 4"
			raise PlanarThinkingException(s)
	
	def apply_to_scene( self, environment ):
		""" Draws the line onto a canvas """
		ltk = environment['ltk']

		# transform the polygon from world coordinates to scene coordinates
		line = environment['local_transformation_matrix'].form_line( self )
		line = environment['global_transformation_matrix'].form_line( line )
		line = environment['view_transformation_matrix'].form_line( line )
		line.homoginize()
		
		coords = line.coordinates.astype(int)
		
		Lilac.create_line(ltk.config('pixels'),ltk.config('zbuffer'),-1,
			coords[0,0], coords[0,1], coords[0,2],
			coords[1,0], coords[1,1], coords[1,2],
			line.color[0], line.color[1],line.color[2])		
			
class PlanarThinkingException(Exception):
	""" Exception thrown by misconfigured line """
	pass