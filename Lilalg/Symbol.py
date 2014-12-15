""" This class is symbols for Array logical-comprehension
	Author: Matthew Levine
"""
class Symbol:
	""" The __sym__ class is an internal class used for list and logical
		comprehension within indexing operation. It should never be created
		by a user; one is provided as a class field in Array, named "x"
	"""
	
	def __init__( self, logical = None, type = 'value' ):
		# we don't use a default argument of [[]] to prevent closure over
		# it
		self.logical = [[]] if logical is None else logical
		self.type = type if (type == 'value' or type == 'index') else None
		
	def __eq__( self, other ):
		""" This completely violates any semi-useful definition of equality.
			You cannot compare the __sym__ object to another object and get
			good (symmetric, non-exception, e.g.) or even logical things
			to happen.
		"""
		logical = [logic[:] for logic in self.logical]
		logical[-1].append( (self.equals,other) )
		return Symbol(logical,self.type)
		
	def __lt__( self, other ): 
		logical = [logic[:] for logic in self.logical]
		logical[-1].append( (self.less_than,other) )
		return Symbol(logical,self.type)
	
	def __leq__( self, other ): 
		logical = [logic[:] for logic in self.logical]
		logical[-1].append( (self.less_than_eq,other) )
		return Symbol(logical,self.type)
	
	def __gt__( self, other ): 
		logical = [logic[:] for logic in self.logical]
		logical[-1].append( (self.greater_than,other) )
		return Symbol(logical,self.type)
	
	def __geq__( self, other ):
		logical = [logic[:] for logic in self.logical]
		logical[-1].append( (self.greater_than_eq,other) )
		return Symbol(logical,self.type)
	
	def __or__( self, other ): 
		[self.logical.append(logic) for logic in other.logical]
		return self
	
	@staticmethod
	def equals( a, b ): return a == b
	
	@staticmethod
	def not_equals( a, b ): return a != b
	
	@staticmethod
	def greater_than( a, b ): return a > b
	
	@staticmethod
	def less_than( a, b ): return a < b
	
	@staticmethod
	def less_than_eq( a, b ): return a <= b
	
	@staticmethod
	def greater_than_eq( a, b ): return a >= b
			
	def is_symbolic(self):
		""" Returns the symbolic category - either value or index, ussually - 
			of the symbol
		"""
		return self.type
		
	def __repr__( self ): return "<Symbol: x>"