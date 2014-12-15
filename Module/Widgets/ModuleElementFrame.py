"""
	This file contains a tk Frame extension for displaying information
	about moduleelements in a UI
	
	Author: Matthew Levine
	Date: 09/23/2014
"""

from tkinter.ttk import Frame

class ModuleElementFrame(Frame):

	def __init__( self, *args, **kwargs ):
		""" Instantiates the widget and makes it size invariant to new widgets """
		Frame.__init__( self, *args, **kwargs )
		self.grid_propagate(False)
	
	def populate( self, fields ):
		""" Tiles the fields into the widget """
		for i,field in enumerate(fields):
			field.grid(column=i%2,row=i//2,sticky='nsew')