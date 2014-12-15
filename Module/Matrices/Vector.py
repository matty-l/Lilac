"""
	This file contains a vector class.
	
	Author: Matthew Levine
	Date: 09/04/2014
"""

from numpy import ndarray, cross as npcross, dot as npdot, array
from math import sqrt

class ModuleVector(ndarray):
	""" This class wraps a numpy array for use as a Lilac-Module Vector 
		
		An alternative implementation would hold internally a nunmpy vector instead
		of extending one, though the current implementation resutls in much less code,
		fewer reference follows (which, in Python, matters where we want performance),
		and allows us to directly pass this to the C underpinnings of Lilac, which
		is very nice.
		
		You might notice that the subclass is slightly nonconventional (the use
		of new instead of init, e.g.) This follows the subclassing of a C 
		extension. See http://docs.scipy.org/doc/numpy/user/basics.subclassing.html
		for details. This allows our Pythonic vector class to have the efficiency
		of a C struct with nominal overhead.
	"""
	
	def __new__( self, x, y, z , h = 0.0 ):
		""" Initializes the vector. The three required values are the x,y, and 
			z values of the vector. The last optional argument is the homogenous 
			coordinate for quaternion algebra. 
		"""
		return ndarray.__new__( self, (4,), buffer=array([x,y,z,h]) )
			
	def normalize( self ):
		""" Reduces the vector to unit length by dividing it by its magnitude """
		# There are faster ways to normalize many vectors at once, but this
		# is fine for just normalizing a few iteratively. numpy.linalg.norm is
		# not efficient for this task. See:
		# http://stackoverflow.com/questions/9171158/how-do-you-get-the-magnitude-of-a-vector-in-numpy
		x,y,z = self[:3]
		length = sqrt( x*x + y*y + z*z )
		self[:3] = self[:3] / length
		
	def cross( self, vector ):
		""" Returns the cross product of this vector and the given vector """
		return ModuleVector( *npcross( self[:3], vector[:3] ) )
		
	def dot( self, vector ):
		""" Returns the dot product of this vector and the given vector """
		return npdot( self, vector ) # homogenous doesn't matter
		
	def as_vector( self ):
		""" Returns the vector; for used in polymorphic type validation """
		# the pythonicness of this method is suspecct
		return self
		
if __name__ == '__main__':
	print("Testing Vector class")
	import numpy as np
	
	v = ModuleVector(1,2,3)
	v2 = ModuleVector(3,4,5)
	print("V1, V2: ",v,v2)
	print("V1+V2: ", np.add(v,v2))
	v.normalize()
	print("V1, normalized: ", v)