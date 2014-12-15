"""
	This file contains a Polyline class
	
	... I don't remember what Bruce meant by Polyline, but this just lets
	you draw lots of lines really quickly.
	
	Author: Matthew Levine
	Date: 09/04/2014
"""

import numpy as np
from Module.Shapes.Shape import Shape
import Lilac

class PolyLine(Shape):
	""" This class defines a polyline in space """
	 
	def __init__( self, starts = np.array([0,0,0,1]),
						ends = np.array([0,0,0,1]),
						color = np.array([0,0,0,0])  ):
		""" Initializes the polyline """
		Shape.__init__(self)
		self.coordinates = starts
		self.coordinates_ends = ends
		self.color = color
		
		if self.coordinates.shape[1] != 4 or color.shape[1] != 4:
			s = "Color data must be in rgba form; points in line must be dim 4"
			raise PolygomousLinearityException(s)
	
	def apply_to_scene( self, environment ):
		""" Draws the polyline onto a canvas """
		ltk = environment['ltk']

		# transform the polygon from world coordinates to scene coordinates
		line = environment['local_transformation_matrix'].form_polyline( self )
		line = environment['global_transformation_matrix'].form_polyline( line )
		line = environment['view_transformation_matrix'].form_polyline( line )
		line.homoginize()
		
		coords = line.coordinates.astype(int)
		coords_ends = line.coordinates_ends.astype(int)
		Lilac.create_lines(ltk.config('pixels'),ltk.config('zbuffer'),
			coords, coords_ends, line.color )

	def homoginize( self ):
		""" Overwrites default homoginization to account for extra coordinate
			set.
		"""
		self.coordinates /= self.coordinates[:,3][:,np.newaxis]
		self.coordinates_ends /= self.coordinates_ends[:,3][:,np.newaxis]

class PolygomousLinearityException(Exception):
	""" Exception thrown by misconfigured polyline """
	pass