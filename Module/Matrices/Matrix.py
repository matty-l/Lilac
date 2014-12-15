"""

	This file contains a class which holds matrix based operations for use in 
	transforming shapes in a Lilac Tk interface system.
	
	Author: Matthew Levine
	Date: 09/04/2014

"""

from numpy import identity as id, sin, cos, zeros, array
from Module.ModuleElement import ModuleElement
from Module.Shapes.Point import Point
from Module.Shapes.Line import Line
from Module.Shapes.PolyLine import PolyLine
from Module.Matrices.Vector import ModuleVector as Vector

from Module.ClassUtils import Overrides

# for convenience define module-level constants
ltm = 'local_transformation_matrix'

class ViewTransformationMatrix(ModuleElement):
	""" This class performs linear algebraic transformations.

		The related ModuleVector class is an extension of a numpy array;
		this class, rather, extends a ModuleElemet. See ModuleVector for 
		an explanation of its implementation. In this case, we had two alternatives:
			- (1) extend array, contain module element
			- (2) extend both ModuleElement and numpy.array
		Containing a module element would be inconsistent with any other uses
		of the class, and indeed since the ModuleElement class is abstract,
		would not make sense. Extending array would makes some operations more
		logical and concise. However, this class is not a matrix. It is a wrapper
		on C matrices that applies them to other C matrices. We make this distinction
		through our implementation.
		
		The difference between an array and array wrapper manifests itself in
		non-trivial ways. External elements are not expected to link directly
		to the underlying matrix in this class. One side-effect is that when methods
		such as "identity" are called, a new identity matrix is overlaid onto 
		the old transformation; any pointers to the old transformation are
		now outdated. Operations called on the wrapper are not guaranteed to
		occur in place.
		
		Getters and setters are not provided as there are no side-effects associated
		with simply pulling a value or assigning it to the internal transformation.
		Where links to that transform should not be assigned, direct access
		is encouraged in this setting.
		
		I probably should have done my algebra a little better to avoid weird
		transpositions in a few functions. Fixme.Also, Vtm, Ltm, Gtm, etc.,
		should be composed BEFORE modifying shapes, because that will be faster
		EDIT: This is done in-line in a lot of places. This version is included
		here for portability, but substituting numpy for LiLalg produces big
		performance increases (and the coolness factor of having done things
		ourself!)
	"""
	__id__ = 0
	
	def __init__( self, transform = None ):
		""" Initializes an identity transform """
		ModuleElement.__init__( self )
		self.transform = id(4) if transform == None else transform
		self.id = ['Matrix',ViewTransformationMatrix.__id__]
		ViewTransformationMatrix.__id__ += 1
		
	def clear( self ):
		""" Clears the transformation """
		self.transform = zeros(4)
		
	def identity( self ):
		""" Sets the transformation to the identity."""
		self.transform = id(4)
		
	def copy( self ):
		""" Returns a copy of the matrix transformation """
		return ViewTransformationMatrix(self.transform.copy())
		
	def transpose( self ):
		""" Transposes the transformation """
		self.transform = self.transform.transpose()
		
	def multiply( self, matrix ):
		""" Multiplies the transform by the given matrix """
		self.transform = matrix.dot(self.transform)
		
	def form_point( self, point ):
		""" Solves mtx * point = X for the given point and transformation
			matrix, returning X as a point. Assumes correct dimensions.
		"""
		
		return Point().from_values(self.transform.dot(point.coordinates),color=point.color)
		
		
	def form_vector( self, vector ):
		""" Solves mtx * vector = X for the given vector and internalized
			transformation matrix and returns X as a vector. Assumes
			correct dimensionality.
		"""
		coords = self.transform.dot(vector)
		return Vector(coords[0],coords[1],coords[2],h=coords[3])
		
	def form_polygon( self, polygon ):
		""" Transforms the points and surface normals (if they exist) in the
			Polygon by the internalized matrix. Returns the polygon, transformed,
			though not in place.
			
			Unlike other like functions (form_line, form_vector, etc.), the 
			input polygon is modified in the course of the operation.
		"""
		trans = self.transform.transpose()
		polygon.coordinates = polygon.coordinates.dot(trans)
		polygon.normals = polygon.normals.dot(trans)
		
	def form_pointcloud( self, cloud ):
		""" Transforms the points  by the internalized matrix. 
			Returns the point cloud, transformed, though not in place.
			
			Unlike other like functions (form_line, form_vector, etc.), the 
			input cloud is modified in the course of the operation.
		"""
		cloud.coordinates = cloud.coordinates.dot(self.transform.transpose())
		
	def form_line( self, line ):
		""" Transforms the points in the given line by the internalized 
			transformation matrix, not in place.
		"""
		return Line( coords = line.coordinates.dot(self.transform.transpose()),
			color = line.color, pad = False )
			
	def form_polyline( self, line ):
		""" Transforms the points in the given polyline by the internalized 
			transformation matrix, not in place.
		"""
		return PolyLine( starts = line.coordinates.dot(self.transform.transpose()),
			ends = line.coordinates_ends.dot(self.transform.transpose()),
			color = line.color )
		
	def scale2D( self, sx, sy ):
		""" Premultiply the matrix by a scale matrix parametrized by sx and sy """
		self.transform = array([ [sx,0,0,0],[0,sy,0,0],[0,0,1,0],
			[0,0,0,1] ]).dot( self.transform )
	
	def scale( self, sx, sy, sz ):
		""" Premultiply the matrix by a scale matrix """
		self.transform = array([ [sx,0,0,0],[0,sy,0,0],[0,0,sz,0],
			[0,0,0,1] ]).dot( self.transform )

			
	def rotateZ( self, cth, sth ):
		""" Premultiply the matrix by z-axis rotation matrix parametrized by
			cos(theta) and sin(theta) where theta is the angle of rotation about
			the Z-axis
		"""
		self.transform = array([[cth,-sth,0,0],[sth,cth,0,0],[0,0,1,0],
			[0,0,0,1]]).dot(self.transform)
			
	def translate2D( self, tx, ty ):
		""" Premultiply the matrix by a 2D translation matrix parametrized
			by tx, ty
		"""
		self.transform = array([[1,0,0,tx],[0,1,0,ty],[0,0,1,0],
			[0,0,0,1]]).dot(self.transform)
			
	def shear2D(self,shx,shy):
		""" Premultiply the transformation by the 2D shear matrix parametrized 
			by shx and shy
		"""
		self.transform = array([[1,shx,0,0],[shy,1,0,0],[0,0,1,0],
			[0,0,0,1]]).dot(self.transform)
			
	def shearZ( self, shx, shy ):
		""" Premultiply the matrix b a shear Z matrix parametrized by shx and shy """
		self.transform = array([[1,0,shx,0],[0,1,shy,0],[0,0,1,0],
			[0,0,0,1]]).dot(self.transform)
			
	def perspective( self, d ):
		""" Premultiply the matrix by a perspective matrix parameterized by d """
		self.transform = array([[1,0,0,0],[0,1,0,0],[0,0,1,0],
			[0,0,1/d,0]]).dot(self.transform)

			
	def rotateX( self, cth, sth ):
		""" Premultiply the matrix by x-axis rotation matrix parametrized by
			cos(theta) and sin(theta) where theta is the angle of rotation about
			the x-axis
			
			Be careful; the angle of cosine and sine must add to one by trig
			identity, but that is not enforced here for performance reasons.
			This function will not produce a rotation if non-trigometrically related
			values are passed.
		"""
		self.transform = array([[1,0,0,0],[0,cth,-sth,0],[0,sth,cth,0],
			[0,0,0,1]]).dot(self.transform)
			
	def rotateY( self, cth, sth ):
		""" Premultiply the matrix by y-axis rotation matrix parametrized by
			cos(theta) and sin(theta) where theta is the angle of rotation about
			the y-axis
			
		"""
		self.transform = array([[cth,0,sth,0],[0,1,0,0],[-sth,0,cth,0],
			[0,0,0,1]]).dot(self.transform)
			
	def rotateXYZ( self, u, v, w ):
		""" Premultiply the matrix by an xyz-axis rotation matrix parameterized
			by orthogonal basis vectors.
		"""
		self.transform = array([[u[0],u[1],u[2],0],[v[0],v[1],v[2],0],
							[w[0],w[1],w[2],0],[0,0,0,1]]).dot(self.transform)
							
	def translate( self, tx, ty, tz ):
		""" Translates the internalized transform about the given axes """
		self.transform = array([[1,0,0,tx],[0,1,0,ty],[0,0,1,tz],
			[0,0,0,1]]).dot(self.transform)
			
	@Overrides(ModuleElement)
	def apply_to_scene( self, environment ):
		""" Applies the matrix to a module environment """
		new_ltm = ViewTransformationMatrix()
		new_ltm.transform = self.transform.dot( environment[ltm].transform )
		environment[ltm] = new_ltm
	
	@Overrides(ModuleElement)
	def accept( self, visitor ):
		""" Applies the visitor pattern for matrices """
		visitor.visit_matrix(self)
			
	def __str__( self ):
		""" Returns a string representation of the transformation """
		return '<Matrix : '+str(self.id)+'>'
		
	def __getitem__( self, indices ):
		""" Supports direct access to transformation values """
		return self.transform[indices]
	
	def __setitem__( self, indices, values ):
		""" Supports direct transformation item assignment """
		self.transform[indices] = values

class IdentityMatrix( ViewTransformationMatrix ):
	""" This matrix is the same as its parent Matrix class, except that
		when looked at by a Module resets the local transformation matrix.
		
		It is assumed that you will never change this from an identity matrix
		internally. This is python, we are trusting.
	"""
	def __init__( self ):
		""" Initializes the identity matrix """
		ViewTransformationMatrix.__init__( self, transform = None )
	
	@Overrides(ModuleElement)
	def apply_to_scene( self, environment ):
		environment[ltm].transform = self.transform.copy()
