"""
	This simple widget allows for renaming an elmenet through
	a popup gui.
	
	Author: Matthew Levine
	Date: 11/21/2014
"""

from tkinter import Toplevel, Entry

class RenameWindow(Toplevel):
	""" This class is a dialog for renaming modules """
	
	def __init__( self, module ):
		Toplevel.__init__( self )
		self.attributes("-alpha", 0.5)
		self.module = module
		self.entry = Entry( self, text = module.id[0] )
		self.entry.grid()
		
		self.bind( "<Return>", self.submit )
		
		
	def submit( self, event = None ):
		""" Finalizes the new name """
		self.module.id[0] = self.entry.get()
		self.destroy()