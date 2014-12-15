"""
	This file contains a view transformation class for 2D projections.
	
	Author: Matthew Levine
	Date: 09/07/2015
"""
from Module.Matrices.Vector import ModuleVector as Vec
from Module.Matrices.Matrix import ViewTransformationMatrix as Mtx

class View2D:
	def __init__( self, Vo = Vec(0,0,0), orientation = Vec(1,0,0), width = 2,
			cols = 500, rows = 500 ):
		""" Creates a new View2D object.
		
			The arguments are:
				- Vo  the center of the view in world coordinates
				- width The width of the view rectangle in world coordinates
				- orientation The orientation of the projection as a normalized vector
				- cols the number of columns in the output image
				
		"""
		self._camera = {
			'Vo' : Vo.as_vector(), 'norm' : orientation.as_vector(), 
			'C':cols, 'R':rows, 'du' : width
		}
		
	def config( self, *args ):
		""" Returns the values of the arguments given as a generator """
		return (self._camera[arg] for arg in args) if len(args) > 0 else self._camera.keys()
				
		
	def setView2D( self, vtm = Mtx() ):
		""" Sets the vtm to the given view transformation matrix """
		R, C, Vo, du, norm = self.config('R','C','Vo','du','norm') 
		dv = du * R / C
		vtm.translate2D( -Vo[0], -Vo[1] ) # translate origin
		vtm.scale2D( C / du, -R / dv ) # scale to normalized window size
		vtm.rotateZ( norm[0], -norm[1] ) # rotate to camera view
		vtm.translate2D( C / 2, R / 2 ) # center at origin of screen
		
		self._camera['vtm'] = vtm
		vtm.camera = self # tricksy cyclical hack, done with care
		return vtm