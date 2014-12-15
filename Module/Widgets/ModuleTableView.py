"""
	The file contains a widget manager for adding a table view to the DesktopController.
	It also instantiates controls over the table and links the GUI to the
	table events.
	
	Author: Matthew Levine
	Date: 09/23/2014
"""

import tkinter as tk

from Module.Visitors.TableVisitor import TableVisitor
from Module.Visitors.FieldVisitor import FieldVisitor
from Module.Widgets.Table import Table
from Module.Widgets.ModuleElementFrame import ModuleElementFrame


class ModuleViewTable(tk.Frame):

	def __init__(self, root, scene ):
		tk.Frame.__init__(self,root)
		self.__build(scene)
	
	
	def __build( self, scene ):
		table = Table(self,width=480,height=32)
		table.grid(sticky='nsew',column=1,row=0)
		def on_selection_change( new_selection ):
			""" Close selected items it if applicable """
			tb = TableVisitor()
			tb.get_table_info(scene,exclusions=table.open_chart)
			table.set_data(tb.display_info)
				
		def on_right_click( right_clicked_item ):
			""" Bring up field table """
			fv = FieldVisitor()
			fv.get_element_info(editor,right_clicked_item[0])
			editor.populate(fv.fields)
			
		table.selection_property.add_listener(on_selection_change)
		table.button3_property.add_listener(on_right_click)
				
		tb = TableVisitor()
		tb.get_table_info(scene)
		table.set_data(tb.display_info)
		
		editor = ModuleElementFrame(self,height=175,width=480)#,background='darkgray',relief='sunken',borderwidth=3)
		editor.grid(sticky='s',column=1,row=0)