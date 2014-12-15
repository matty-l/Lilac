"""
	This file contains a PointCloud class
	
	Author: Matthew Levine
	Date: 09/04/2014
"""

import numpy as np
from Module.Shapes.Shape import Shape
import Lilac

class PointCloud(Shape):
	""" This class defines a point cloud in space """
	
	def __init__( self, coords = np.array([0,0,0]), color = np.array([0,0,0,0]),
						radii = 5 ):
		""" Initializes the point """
		Shape.__init__(self)
		self.coordinates = np.pad(coords,((0,0),(0,1)),'constant',constant_values=1)
		self.color = color
		self.radii = radii
		if self.coordinates.shape[1] != 4 or self.coordinates.shape != color.shape:
			s = "Color (rgba form) and cloud data must match in shape"
			raise CloudyThinkingException(s)
	
	def apply_to_scene( self, environment ):
		""" Draws the point onto a canvas """
		
		ltk = environment['ltk']

		# transform the polygon from world coordinates to scene coordinates
		environment['local_transformation_matrix'].form_pointcloud( self )
		environment['global_transformation_matrix'].form_pointcloud( self )
		environment['view_transformation_matrix'].form_pointcloud( self )
		self.homoginize()
		
		coords = self.coordinates.astype(int)
		
		Lilac.create_point_cloud(ltk.config('pixels'),coords,self.color,
							self.radii)	

class CloudyThinkingException(Exception):
	""" Exception thrown by misconfigured point cloud """
	pass