"""
	This file contains a class that generates a Sphere Modular mesh. 
	
	The
	constructor tries to perform the most efficient construction possible at
	each iteration, adding its own cache process on top of the ShapeFactory's
	cache. In order of prioritization, the Generator will 1) load a sphere
	of the requested detail from memory, 2) unpickle a sphere in memory,
	or 3) generate the sphere dynamically. This can be computationally expensive;
	the major limit is memory, and since this is only done as a last choice, we
	accept Python for its implementation.
		
	Author: Matthew Levine
	Date: 09/04/2014
"""

import numpy as np
from PIL import Image
from Module.ModuleElement import ModuleElement
from Module.Module import Module
from Module.Matrices.Matrix import ViewTransformationMatrix as Mtx
from Module.Shapes.Polygon import Polygon
import Lilac
from math import sqrt, cos, sin, pi
import math

from Module.Shapes.ObjGenerator import ObjGenerator
from Module.ClassUtils import Overrides

import pickle

G = ( 1 + sqrt(5) ) / 2

class SphereGenerator(ObjGenerator):
	""" This class defines a sphere in space """
	 
	__cache__ = 0
	pickle = 0
	 
	def __init__( self, recursion = 3, texture = 0 ):
		""" Initializes the polygon """
		ObjGenerator.__init__(self)
		
		if not SphereGenerator.__cache__:
			# try to unpickle it
			try:
				if not SphereGenerator.pickle:
					raise IOError("custom")
				sp = open('Module/Objects/sphere'+str(recursion)+'.p','rb')
				self.mesh =pickle.load(sp)
			except IOError as e:
				self.polygons = []
				self.build_mesh()
				
				for i in range(recursion):
					self._subdivide()
					
				SphereGenerator.__cache__ = self.polygons
		else:
			for poly in SphereGenerator.__cache__:
				vec = np.array(poly)
				self.mesh.add_shape(Polygon(coords=vec,normals=get_normal(vec)))
	
		if texture:
			SphereGenerator.texture_sphere(self.mesh,texture)
			
		self.mesh.invisible = 'gouroud'
					
	@Overrides(ObjGenerator)
	def build_mesh( self ):
		sides = []
		
		v = [
			[-1,G,0,1],[1,G,0,1],[-1,-G,0,1],[1,-G,0,1],
			[0,-1,G,1],[0,1,G,1], [0,-1,-G,1],[0,1,-G,1],
			[G,0,-1,1],[G,0,1,1],[-G,0,-1,1],[-G,0,1,1]  ]
			
		# normalize the points
		for i,point in enumerate(v):
			mag = sqrt(point[0]*point[0]+point[1]*point[1]+point[2]*point[2])
			v[i] = [point[0]/mag,point[1]/mag,point[2]/mag,1]
		
		sides.append([v[0],v[11],v[5]])
		sides.append([v[0],v[5],v[1]])
		sides.append([v[0],v[1],v[7]])
		sides.append([v[0],v[7],v[10]])
		sides.append([v[0],v[10],v[11]])
		
		sides.append([v[1],v[5],v[9]])
		sides.append([v[5],v[11],v[4]])
		sides.append([v[11],v[10],v[2]])
		sides.append([v[10],v[7],v[6]])
		sides.append([v[7],v[1],v[8]])
					
		sides.append([v[3],v[9],v[4]])
		sides.append([v[3],v[4],v[2]])
		sides.append([v[3],v[2],v[6]])
		sides.append([v[3],v[6],v[8]])
		sides.append([v[3],v[8],v[9]])
		
		sides.append([v[4],v[9],v[5]])
		sides.append([v[2],v[4],v[11]])
		sides.append([v[6],v[2],v[10]])
		sides.append([v[8],v[6],v[7]])
		sides.append([v[9],v[8],v[1]])
		
		for side in sides:
			self.mesh.add_shape(self._gen_poly(side,side))
			self.polygons.append(side)
	
	def _getMidpoint( self, p1, p2 ):
		point = [ p1[0]/2+p2[0]/2, p1[1]/2+p2[1]/2, p1[2]/2+p2[2]/2, 1 ]
		mag = sqrt( point[0]*point[0] + point[1]*point[1] + point[2]*point[2] )
		point = [point[0]/mag,point[1]/mag,point[2]/mag,1]
		return point
				
		
	def _subdivide( self ):
		faces = []
		mesh = Module()
		for face in self.polygons:
			
			a = self._getMidpoint( face[0], face[1])
			b = self._getMidpoint( face[1], face[2] )
			c = self._getMidpoint( face[0], face[2] )
			
			faces.append( [face[0],a,c] )
			faces.append( [face[1],b,a] )
			faces.append( [face[2],c,b] )
			faces.append( [a,b,c])

		self.polygons = faces
		for face in faces:
			mesh.add_shape(self._gen_poly(face,face))

		self.mesh =  mesh

	def texture_sphere( sphere, filename ):
		""" Statically texturizes the given sphere using the
			texture in the file indicated by the given file name
		"""

		# do some formatting
		if not filename.startswith('images/'):
			filename = 'images/'+filename
		# load the texture
		try:
			tex = np.array(Image.open(filename))
		except Exception as e:
			raise UnshapelyException("Unidentified flying texture "+str(filename))
								
		# handle optimized and non-optimized form, for efficient pickling
		if len(sphere.__elements__[0].coordinates.shape) == 2:
			for i,poly in enumerate(sphere.__elements__):

				try:
					poly.texture
				except: continue
				
				vn = poly.coordinates[0]
				r = sqrt( vn[0]*vn[0] + vn[1]*vn[1] + vn[2]*vn[2] )
				u = .5 + math.atan2( vn[2]/r, vn[0]/r ) / (2 * math.pi )
				v = .5 - math.asin( vn[1] / r ) / math.pi
				
				lon = tex.shape[0] * v - 1
				lat = tex.shape[1] * u - 1
				
				try:
					poly.texture = np.array(list(tex[int(lon),int(lat)]) +[255])
				except TypeError: # account for greyscale images
					poly.texture = np.array([tex[int(lat),
						int(lon)]for i in range(3)] +[255])
			# sphere.optimize()
		else:

			poly = sphere.__elements__[0]
			for i,vn in enumerate(poly.coordinates):
				# code duplication is bad..
				vn = vn[0]
				r = sqrt( vn[0]*vn[0] + vn[1]*vn[1] + vn[2]*vn[2] )
				lat = math.degrees(math.asin(vn[1]/r))
				lon = math.degrees(math.atan2(vn[0],vn[2]))
				
				lon = tex.shape[1]/2+tex.shape[1]/2*(lon/180) - 1
				lat = tex.shape[0]/2+tex.shape[0]/2*(lat/180) - 1
				
				try:
					poly.texture[i] = np.array(list(tex[int(lat),int(lon)]) +[255])
				except TypeError: # account for greyscale images
					poly.texture[i] = np.array([tex[int(lat),
						int(lon)]for i in range(3)] +[255])
						
	def _gen_poly( self, coords, normals ):
		# FIXME: do this yourself, super slow right now
		cn = coords[0]
		r = sqrt(cn[0]*cn[0]+cn[1]*cn[1]+cn[2]*cn[2])
		u = int(255 * (.5 + math.atan2( cn[2]/r, cn[0]/r ) / (2 * math.pi )))
		v = int( 255 * (.5 - math.asin( cn[1] / r ) / math.pi) )
		anchor = np.array([[u,v,-1,-1],[u-1,v,-1,-1],[u,v-1,-1,-1]]).flatten().astype(int)
		# print(anchor)
		return Polygon( np.array(coords),normals=get_normal(normals),anchor=anchor)
		
def get_normal( coords ):
	""" Returns a normal from a set of coorinates """
	return np.array(coords)
	# tmp = np.array(coords)
	# norm = -np.cross( tmp[1,:3] - tmp[0,:3], tmp[2,:3] - tmp[0,:3] )
	# norm = np.array(norm.tolist() + [0])
	# return norm
	
class UnshapelyException(Exception):
	""" Exception thrown by misconfigured polyline """
	pass