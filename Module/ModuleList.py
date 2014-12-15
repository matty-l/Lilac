"""
	This file contains a special class for managing lists.
	
	This violates the Liskov substitution rule pretty blatantly. Since
	things are duck-typed, however, I don't think this applies.
	
	Author: Matthew Levine
	Date: 09/12/2014
"""

class ModuleList(list):
	
	def __getitem__( self, key ):
		""" Returns the item in the list by the actual index (if an
			integer) or by the "index" field if an object. Raises
			a TypeError if incompatible with both.
		"""
		try:
			return super(ModuleList,self).__getitem__(key)
		except TypeError:
			try:
				return super(ModuleList,self).__getitem__(key.index)
			except AttributeError:
				raise TypeError("list indices must be integers or Modules, not "\
					+str(key.__class__))
					
if __name__ == '__main__':
	m = ModuleList([1,2,3])
	print(m)
	print(m[0])
	class Foo: index = 1
	class Bar: pass
	print(m[Foo()])
	print(m[Bar()])