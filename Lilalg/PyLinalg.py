"""
	Fast C-based linear algebra package optimized for graphics.
	
	Python front-end includes slice retrieval and logical indexing
	
	Author: Matthew Levine
	Date: 10/2/2014
"""

import Lilalg as llg
from Symbol import Symbol

class Array:
	__sym__ = Symbol
	
	@property
	def x(self): 
		return Array.__sym__(type='value')
		
	@property
	def i(self):
		return Array.__sym__(type='index')

	def __init__( self, data = None ):	
		""" Creates a new array and allocates underlying heap
			memory
		"""
		self.index = llg.create_array()		
		if data is not None:
			[[llg.set_data(self.index,i,j,val) for j,
			val in enumerate(sublist)] for i,sublist in enumerate(data)]
				
		
	def __del__( self ):
		""" Clears the underlying heap memory when this object gets
			garbage collected
		"""
		llg.free_array( self.index )
		
	def __getitem__( self, arg ):
		""" Returns the element at the indiciated position in the array """
		data = llg.get_data(self.index)
		# try assuming of form mtx[a,b]
		try:
			return data[arg[0] * 4 + arg[1]]
		except TypeError: pass
		
		# try assuming of the form mtx[a]
		try:
			itx = arg * 4
			return [data[itx],data[itx+1],data[itx+2],data[itx+3]]
		except TypeError:pass
		
		# try assuming slicing arguments
		indices = []
		for i in range(2):
			try:
				# see if we're slicing by looking at the index
				start = arg[i].start if arg[i].start is not None else 0
				stop = arg[i].stop if arg[i].stop is not None else 4
				step = arg[i].step if arg[i].step is not None else 1
				indices.append( range(start,stop,step) )
			except (TypeError, AttributeError):
				indices.append( (arg[i],) )
		return [[data[row*4+col] for col in indices[1]] for row in indices[0]]
		
	def __setitem__( self, arg, val ):
		""" Set the item at the given index. Indicies can be logical, list
			or generator comprehensible, or integral. Value mut be natively
			convertible to a floating points value and match the dimension
			of the input
		"""
		try:
			if len(arg) != 2: raise TypeError("")
			[float(val),int(arg[0]),int(arg[1])]
			llg.set_data(self.index,arg[0],arg[1],float(val))
			return
		except: pass
		
		# allow for logical indexing
		data = llg.get_data(self.index)
		try:
			# duck type only accept symbolic arguments in this clause
			arg.is_symbolic()
			# loop over all input expressions and validate their condition per term
			for expression in arg.logical:
				for index, value in enumerate(data):
					# allow for indexing by key or by value
					objective = index if arg.is_symbolic() == 'index' else value
					# set the element to the value if all conditions are met on it
					if all([function(objective,other) for (function,other) in expression]):
						llg.set_element(self.index, index, val)				
		except:
			raise Array.Exception("Invalid arguments",arg,val,"when setting matrix value")
		
	def __repr__( self ):
		""" Returns a useful string representation of the array """
		data = llg.get_data(self.index)
		return '\n'.join([', '.join(['%07.3f'%data[i*4+j] for j in range(4)]) for i in range(4)])
		
	def __mul__( self, other ):
		""" Term-wise this matrix by the other matrix """
		out = Array()
		try:
			other.x
			llg.multiply(self.index,other.index,out.index)			
			return out
		except AttributeError: pass
		
		try:
			llg.scale(self.index,out.index,float(other))
		except:
			raise Array.Exception("Undefined multiplication operation")
		
		return out
				
	class Exception(Exception): pass
	
	
class Identity(Array):
	def __init__( self ):
		Array.__init__( self, data = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]] )		
