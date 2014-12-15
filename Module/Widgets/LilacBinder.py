"""
	This file contains a class that takes a LilacTk instance and
	associates useful bindings to it.
	
	Author: Matthew Levine
	Date: 10/13/2014
"""

class LilacBinder:

	def __init__( self ):
		""" Initializes the binder fields """
		self.selects = [(0,0),(0,0)]
		self.rect = None

	def init_all_bindings( self, ltk ):
		""" Initializes all associated bindings with the given LilacTk instance """
		self.canvas = ltk.config("canvas")
		self.bind_mouse_selection(self.canvas)
		
	def bind_mouse_selection( self, canvas ):
		""" Binds the ability to select objects with the mouse """
		canvas.bind('<Button-1>',self.start_rect)
		canvas.bind('<B1-Motion>',self.on_move)
		canvas.bind('<ButtonRelease-1>',self.release_rect)
		
	def start_rect(self, event=None):
		self.selects[0] = [event.x,event.y]		
		
	def on_move(self, event=None):
		if self.rect is not None:
			self.canvas.delete(self.rect)
		self.rect = self.canvas.create_rectangle(self.selects[0][0],
			self.selects[0][1], event.x,event.y,dash=1,width=2,outline='red')
			
	def release_rect(self, event=None):
		if self.rect is not None:
			self.canvas.delete(self.rect)
	