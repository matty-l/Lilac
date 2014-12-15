"""
	This file contains a Grid class built on underyling C management
	for fast step-wise processing.
	
	Author: Matthew Levine
	Date: 12/11/2014
"""
import numpy as np
import LiEmmitor.LiFlame as LiFlame


class Grid():
	
	def __init__(self, width = 500, height = 500):
		LiFlame.grid(width,height)
		self.width = width
		self.height = height
		
	def __getitem__( self, key ):
		""" Returns the value of the temperature of grid at the given index """
		try: (i,j) = key
		except TypeError:
			raise Grid.TypeError("Invalid index into grid during retrieval")
		
		return LiFlame.get_temperature(i,j)

	def __setitem__( self, key, value ):
		""" Sets the value of the temperature of grid at the given index """
		try: (i,j) = key
		except TypeError:
			raise Grid.TypeError("Invalid index into grid during retrieval")

		return LiFlame.set_temperature(int(i),int(j),int(value)-1)

		
	def __call__( self, column = None, row = None, value = None  ):
		""" Returns the value of the concentration of grid at the given index.
			
			This syntax is a little wishy washy, and I'll probably change it.
			If called as grid(x=4,y=5,6), it means "adds to the (4,5)th item the
			value 6; if called as grid(x=4,y=5) it means return the value at 
			(4,5). Particularly confusing is that this is a relative add, not
			an absolute add, since that usage is much more common in our
			application.
		"""
		if column is None or row is None:
			raise Grid.TypeError("Need coordinates to set or get concentration from grid")
		
		if value is not None:
			# set the concentration here. Un-pythonically (but in C style) returns
			# success flag
			error = LiFlame.set_concentration(int(column),int(row),int(value))
			if error <= 0:
				raise Grid.TypeError("Failed to adjust concentration at "+str(column)+\
					","+str(row)+' by '+str(value)+':'+' error code '+str(error))
		else:
			# if no third argument, just return the value at the location
			return LiFlame.get_concentration(column,row)
		
		
	def __del__( self ):
		""" On garbage collection, release the grid """
		LiFlame.degrid()
		
	class TypeError(Exception):pass
	
	def view_temperature( self ):
		""" Returns a numpy array containing the temperature of the grid """
		heat = np.zeros((self.width*self.height),np.uint32)
		if not LiFlame.view_temperature(heat):
			raise Grid.TypeError("Failed to view the temperature")
		return heat.reshape((self.width,self.height))
	
	
	def step(self):
		""" Increments the grid forward in time.
			Decreases the temperature of the grid
		"""
		if not LiFlame.step():
			raise Grid.TypeError("Failed to step the grid")
				

if __name__ == '__main__':
	g = Grid()
	print(g[1,3])
	g(3,3,5)
	print(g(4,4),g(3,3))
	print('\n\n')
	
	g[1,2] = 100
	print(g.view_temperature())