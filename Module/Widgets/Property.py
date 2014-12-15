"""
	This file contains a class that allows for generic variables storage
	while implementing the observer pattern.
	
	Author: Matthew Levine
	Date: 09/20/2014
"""
import inspect

def listener( func ):
	def correct_args(property,oldval,newval):
		num_args = len(inspect.getargspec(func)[0])

		if num_args > 3: 
			raise PropriotaryPropertyException("Listeners cannot have more than 3 arguments")
		elif num_args == 1:
			return func(newval)
		elif num_args == 2:
			return func(oldval,newval)
		else:
			return func(property,oldval,newval)
	return correct_args
	

class Property:
	
	def __init__( self, data = None ):
		""" Creates a new Property with no listeners and an optional
			data element
		"""
		self.data = data
		self.listeners = []
	
	def add_listener( self, function ):
		""" Adds a new listener. The listener must accept three arguments:
			(1) the listener object (2) the old value of a property variable prior
			to a change and (3) the new value of the property variable
			after a change
		"""
		self.listeners.append(listener(function))
		return len(self.listeners) - 1
		
	def remove_listener( self, listener_index ):
		self.listeners.remove(listener_index)
	
	def set( self, data ):
		""" Sets the data to the new value and alerts the listeners """
		[listener(self,self.data,data) for listener in self.listeners]
		self.data = data
		
	def get( self ):
		""" Returs the value from the listener """
		return self.data
		
		
class PropriotaryPropertyException(Exception): pass

if __name__ == '__main__':
	print("Testing properties")
	p = Property("Hat")

	def foo(a,b,c):
		print(a,b,c)
		
	def bar(a,b,c,d):
		print(a,b,c)
		
	def foobar(a,b):
		print(a,b)
		
	p.add_listener(foo)
	p.add_listener(foobar)
	p.set("grat")
	
