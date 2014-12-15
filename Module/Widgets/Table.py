"""
	This file contains a Tkinter widget for tabling information
	
	The tree has a selection property that follows the observer
	pattern for the currently selected element; it has bindings
	for the entry key and mouse presses, and it accomodates
	sorting by column headings.
	
	Edit: sorting by columns headings has been disabled, it
	was distracting.
	
	Author: Matthew Levine
	Date: 09/19/2014
"""

import tkinter.ttk as ttk
import tkinter.font as Font
from functools import cmp_to_key
from Module.Widgets.Property import Property
from Module.Widgets.RenameWindow import RenameWindow

class Table(ttk.Frame):
	""" This class tables information for display in a Tkinter 
		GUI application
	"""
		
	def __init__( self, root, width = 200, height = 100 ):
		""" Initializes the parent frame and the table widget """
		ttk.Frame.__init__(self,root,width=width,height=height)
		
		self.geometry = (width,height)
		self.sorted = -1
		
		# javafx style, crate the tree and an external property wrapping it
		# the tree is the current tree, so s pointer to it could change; that's
		# why it shouldn't be directly accessed (new data means new tree)
		self.__tree = None 
		self.tree_property = Property()		
		self.selection_property = Property()
		self.button3_property = Property()
		
		self.column_titles = ['','Class','Length','   In   ']
		
		self.open_chart = {}
		self.build()
		self.clear()
				
	def build( self ):
		""" Builds the table """
		if self.__tree: self.__tree.pack_forget()
		self.__tree = ttk.Treeview(self,columns=self.column_titles,show='headings',
			height=self.geometry[1])
		self.tree_property.set(self.__tree)
		self.__tree.tag_configure('oddRow',background='gray')
		self.__tree.tag_configure('evenRow',background='yellow')
		
		def on_mouse_right_click(event=None):
			""" Performs update routines on the table's selection when a mouse
				event is detected (must be bound to mouse event on the widget)
			"""
			row = self.__tree.identify('row',event.x,event.y)
			if row:
				data = self.base_data[int(row[1:],16)-1]
				self.open_chart[data[0]] = not self.open_chart[data[0]]
				self.selection_property.set( data )

		def on_mouse_left_click(event=None):
			""" Performs update routines on the table's selection when a mouse
				event is detected (must be bound to mouse event on the widget)
			"""
			row = self.__tree.identify('row',event.x,event.y)
			if row:
				data = self.base_data[int(row[1:],16)-1]
				self.open_chart[data[0]] = not self.open_chart[data[0]]
				self.button3_property.set( data )
				
			
		def on_key_press(event=None):
			""" Performs update routines on the table's selection when a key
				event is detected (must be bound to key event on the widget)
			"""
			row = int(self.__tree.selection()[0][1:],16)-1
			data = self.base_data[row]
			print(data)			
			
		# def selection_update(event=None):
			# """ Updates table's state with last selection """
			# self.selection_property.set(self.get_selection())
			
		self.__tree.bind("<Button-3>", on_mouse_right_click)
		self.__tree.bind("<Button-1>", on_mouse_left_click)
		self.__tree.bind("<Return>", on_key_press)
		self.__tree.bind("<F2>",self.rename_element)
		# self.__tree.bind("<<TreeviewSelect>>", selection_update)
		self.__tree.pack()
		
	def clear( self ):
		""" Clears the table and formats it for data """
		header_width = [Font.Font().measure(col.title()) for col in self.column_titles]
		table_scale = self.geometry[0]/sum(header_width)
		
		for i,column in enumerate(self.column_titles):
			self.__tree.heading(column,text=column.title())
				#command=lambda c=column:self.sort(c))
			self.__tree.column(column,width=int(header_width[i]*table_scale ))
		
		self.sorted_data = []
		
	def sort( self, header_name ):
		""" Sorts the columns of the tree based on the category indicated
			by the parametrized header. This is by default object comparison, i.e.,
			floats will not be converted and compared numerically.
		"""
		head_idx = self.column_titles.index(header_name)
		key = lambda h1,h2: ((h1[head_idx][0]) > (h2[head_idx][0])) * self.sorted
		
		self.sorted_data.sort(key=cmp_to_key(lambda col1,col2 : key(col1,col2) ))
		
		# FIXME: insertion sort to quicksort
		tree_size = len(self.__tree.get_children())
		for newpos,newdata in enumerate(self.sorted_data):
			oldpos = self.table_chart[newdata[0][0]] + 1
			for branch in self.__tree.get_children():
				if int(str(branch[1:]),16) == oldpos:
					self.__tree.move(branch,'',0)
					self.__tree.item(branch,tags=('oddRow')if not newpos%2 else())
					break
		self.sorted = -self.sorted
		
	def set_data( self, data ):
		""" Sets the table data """
		self.build()
		self.clear()
		
		self.sorted_data = data
		self.base_data = data[:]
	
		assert(all([len(el) == len(self.column_titles) - 1 for el in data]))
		self.table_chart = { el[0]:i for i,el in enumerate(data) }
		oc = self.open_chart
		self.open_chart = {el[0]:0 if el[0]not in oc else oc[el[0]]for el in data}
		
		[self.__tree.insert('',0,values=[oc[el[0]]*1 if el[0] in oc else 0]+el,
			tags=['oddRow' for j in range(not i%2)]) for i,el in enumerate(data)]
		
	def get_selection( self ):
		selection_index = int(self.__tree.selection()[0][1:],16) - 1
		if  selection_index < len(self.base_data):
			return self.base_data[selection_index]
		return ()
		
	def rename_element( self, event = None ):
		""" This is a usage-specific function added to support changing the 
			name of elements in the table at runtime, as that functionality 
			is very useful
		"""
		selection = self.get_selection()
		if len(selection) > 0:
			RenameWindow( selection[0] )
