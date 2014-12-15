"""
	This file contains a Polygon class
		
	Author: Matthew Levine
	Date: 09/04/2014
"""

import numpy as np
from Module.Shapes.Shape import Shape
import Lilac
from Module.ClassUtils import Overrides

overwrite = {}

class Polygon(Shape):
	""" This class defines a polygon in space """
	
	__texture__ = 0
	__bump__ = 0
	 
	def __init__( self, coords = np.array([[0,0,0,1]]),
						color = [0,0,0,0], normals = np.array([0,0,0,1]),
						texture=[], anchor=None):
		""" Initializes the polygon """
		Shape.__init__(self)
		self.coordinates = coords
		self.color = color
		self.normals = normals
		self.texture = texture
		self.anchor = anchor
						

	@Overrides(Shape)			
	def apply_to_scene( self, environment ):
		""" Draws the polygon onto a canvas """
		# for legacy imports
		try:
			self.anchor
		except:
			self.anchor = None
		
		(ltk,ds,lighting) = (environment[key] for key in ('ltk','draw_state','lighting'))
		poly = self.copy()
		(ltm,gtm,vtm) = (environment[key] for key in ('local_transformation_matrix',
			'global_transformation_matrix','view_transformation_matrix'))

		if len(self.coordinates.shape) != 2:
			return self.expand_application( ltk,ds,lighting,poly,ltm,gtm,vtm)
			
		# transform the polygon from world coordinates to scene coordinates
		ltm.form_polygon( poly )
		gtm.form_polygon( poly )
		
		# color precedence order is defined, draw-state, texture in ascending
		Lilac.set_alpha(ds['alpha'][0]) # alpha value for alpha blending
		beta = ds['beta'][0]
		# if beta > .25: beta = 1
		Lilac.set_beta(beta)   # beta value for reflections
		Lilac.set_surface_color(*ds['surface_color'][:3])
		color = ds['base_color']
		if color == [None]: color = poly.color
		if poly.texture != []: color = poly.texture

		# apply lights (vrp can be pulled out, here)
		color = np.array(lighting.shade(color,ds['surface_color'],
			poly,ltk.config('camera').camera.config('vrp')))

		if len(poly.normals.shape) == 1:
			(nx,ny,nz) = (poly.normals[i] for i in range(3))
			Lilac.disable_normal_interpollation()
		else:
			p = poly.normals.astype(np.float32)
			(nx,ny,nz) = (0,0,0)
			
			Lilac.enable_normal_interpollation( -1, p, len(poly.normals) )

			
		vtm.form_polygon( poly )
		poly.homoginize()
				
		width,height = ltk.config('width','height')
		texpack = ds['texture']
		bumpmap = ds['bumpmap']
		(tex_defined,bump_defined) = ( el != [None, None] for el in( texpack,bumpmap) )
		if not poly.clip( width, height ): 
			# Texture or bumpmap if (1) Lilac has textures included or we
			# are in the overwrite texture-flag map, (2) we have anchors
			# defined, and (3) there is either a bump map or texture resource
			if (ltk.texture or self in overwrite) and self.anchor != None and (tex_defined or bump_defined):
				Lilac.set_anchor_points(-1,self.anchor,len(poly.coordinates))
				(same_tex,same_bump) = (Polygon.__texture__ == id(texpack[0]),
											Polygon.__bump__ == id(bumpmap[0]))

				if tex_defined and not same_tex:
					Lilac.set_texture(-1,texpack[0],texpack[1][1],texpack[1][0],texpack[1][2])
					Polygon.__texture__ = id(texpack[0])
				elif not tex_defined:
					Lilac.release_textures()
					Polygon.__texture__ = 0
					
				# if we have a texture and it isn't the old texture do A
				# if we do not have a texture do B
				#	we do not have a texture
					
				if bump_defined and not same_bump:
					Lilac.set_bump_map(-1,bumpmap[0],bumpmap[1][1],bumpmap[1][0],bumpmap[1][2])
					Polygon.__bump__ = id(bumpmap[0])
				elif not bump_defined:
					Lilac.release_bump_map()
					Polygon.__bump__ = 0
			else:
				Lilac.release_anchors_and_textures()
				Polygon.__bump__ = Polygon.__texture__ = 0
				
			Lilac.create_polygon( -1, ltk.config('pixels'),
				poly.coordinates.astype(np.float32),  
				ltk.config('zbuffer'), color/255, nx, ny, nz )
	
	def expand_application( self, ltk,ds,lighting,poly,ltm,gtm,vtm ):
		""" Applies the polygon to the scene under conditions in which
			it wraps many local shapes
		"""
		# convert to scene coordinates
		Lilac.preprocess_transformation(0,
				poly.coordinates, poly.normals,
				gtm.transform.astype(float),ltm.transform.astype(float))		
		
		
		# define the color scope
		color = np.array(lighting.multishade(poly.texture,ds['surface_color'],
			poly,ltk.config('camera').camera.config('vrp')))
		
		# apply the view transformation, homoginize, clip, and remove hidden
		# surfaces		
		Lilac.process_view_transform(0,
				poly.coordinates, 
				vtm.transform.astype(float))

		pixels = ltk.config('pixels')
		zbuffer = ltk.config('zbuffer')

		# one-pass scan-line for the whole module
		Lilac.create_polygons( -1, pixels,
				poly.coordinates.astype(np.float32),  zbuffer, color/255 )
	
	@Overrides(Shape)
	def copy( self ):
		""" Returns a deep copy of the Polygon """
		return Polygon( coords = self.coordinates.copy(), color = self.color[:],
							normals = self.normals.copy(), texture=self.texture)
			
			
	@Overrides(Shape)
	def accept( self, visitor ):
		""" Implements the visitor pattern for this polygon """
		visitor.visit_polygon(self)
	
	def __repr__( self ):
		""" Returns a useful representation of this polygon for display """
		return "<Polygon : "+str(self.id)+">"

class NullPolygon(Polygon):
	""" Implements the Null Object Pattern for Polyons """
	__poly = None
	
	def __new__( cls ):
		if not cls.__poly:
			cls.__poly = super(Polygon,cls).__new__(cls)
		return cls.__poly
		
	def __repr__( self ):
		return "..."

NULL_POLYGON = NullPolygon()

class UnshapelyException(Exception):
	""" Exception thrown by misconfigured polyline """
	pass