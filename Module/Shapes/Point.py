"""
	This file contains a Point class
	
	Author: Matthew Levine
	Date: 09/04/2014
"""

import numpy as np
from Module.Shapes.Shape import Shape
import Lilac


class Point(Shape):
	""" This class defines a single point in space """
	__dt__ = 1
	def disable_transforms(): Point.__dt__ = 0
	
	def __init__( self, x = 0, y = 0, z = 0, color = (0,0,0), radii = 5 ):
		""" Initializes the point """
		Shape.__init__(self)
		self.coordinates = np.ascontiguousarray([x,y,z,1])
		self.color = color
		self.radii = radii
	
	def apply_to_scene( self, environment ):
		""" Draws the point onto a canvas """
		ltk = environment['ltk']

		# transform the polygon from world coordinates to scene coordinates
		if self.__dt__:
			pnt = environment['local_transformation_matrix'].form_point( self )
			pnt = environment['global_transformation_matrix'].form_point( pnt )
			pnt = environment['view_transformation_matrix'].form_point( pnt )
			pnt.homoginize()
		else: pnt = self
		
		# print(pnt.coordinates)
		
		coords = pnt.coordinates.astype(int)
		Lilac.create_oval(ltk.config('pixels'), -1,coords[0],coords[1],
			pnt.radii, pnt.color[0],pnt.color[1],pnt.color[2])	
	
	def from_values( self, coordinates, color ):
		self.coordinates = coordinates
		self.color = color
		# what I want is self.coordinates[:4] = coordinates[:4] but it won't work :(
		return self
		
	def homoginize( self ):
		""" Overwrites the default homoginization behavior to account
			for dimension-boundary error
		"""
		self.coordinates /= self.coordinates[3]