"""
	This class creates a terminal widget for use with the
	LilacTk Interface GUI
	
	Author: Matthew Levine
	Date: 09/13/2014
"""

from tkinter import Canvas,Text,END,INSERT,Scrollbar
import sys
from io import StringIO
import traceback
from threading import Timer

# for terminal access
import numpy
import math
from Module.Visitors.FieldVisitor import set_local_scale

# the keycode for backspaces
BACKSPACE = 22
RETURN = 36

class LilacTerminal:

	""" This class allows for direct access to system variables
		through a GUI option, managed by Tk.
	"""
	
	def __init__( self, root, master, width = 68, height = 4 ):
		""" Initilaizes the terminal with the given root pane"""
		widgets = {'canvas':Canvas(root)}
		widgets.update({'entry':Text(widgets['canvas'],
			bg='black',fg='green',insertbackground='white',
			width=width,height=height),
			'scroll':Scrollbar(root)})
			
		widgets['canvas'].grid(column=0,row=0)
		widgets['entry'].config(yscrollcommand=widgets['scroll'].set)		
		widgets['scroll'].config(command=widgets['entry'].yview)
		widgets['scroll'].grid(row=0,column=1,sticky='nsew')
		widgets['entry'].grid(row=0,column=0)
		
		widgets['entry'].insert(INSERT,"Lilac Terminal Online.\n>>")
		
		widgets['entry'].bind('<KeyRelease>',self.validate_line)
		widgets['entry'].bind('<Button-1>',self.validate_line)
		
		self.line_number = 2
		self.widgets = widgets
		self.master = master
		self.__delay__ = 0
		
	def __run__(self, input=""):
		input=input.replace('self','self.master')
		old_out = sys.stdout
		new_out = sys.stdout = StringIO()
		try:
			if input == 'exit()': exit(1)
			if input == 'clear': 
				self.widgets['entry'].delete(2.0,END)
				self.widgets['entry'].insert(END,'\n')
				self.line_number = 2
				return
			
			old_locals = locals().copy() 			
			exec (input,globals(),locals()) # execute the code
			for key,val in locals().items(): # save new variables
				if key != 'old_locals' and key not in old_locals:
					globals()[key] = val
					
		except Exception as e:
			print('Lilac Exception:',str(e),traceback.format_exc())
			
		output = new_out.getvalue()
		self.widgets['entry'].insert(END,'\n'+output)
		self.line_number += output.count('\n')+1
		self.widgets['entry'].see(END)
		
		sys.stdout = old_out
		
	def eval_next_line( self, event = None ):
		""" Evaluates the next line """
		entry = self.widgets['entry']
		

		index  = str(int((entry.index(INSERT)).split('.')[0])-1)
		
		# error check
		if entry.get(index+'.0',index+'.2') != '>>':
			return entry.delete(index+'.0',index+'.999999')
		if int(index) != self.line_number: return
		self.line_number+=1
		
		# run the code
		self.__run__(entry.get(index+'.2',index+'.9999999'))
		entry.insert('end','>>')
				
	def validate_line( self, event = None ):
		if event.keycode == RETURN:
			return self.eval_next_line(event)

		entry= self.widgets['entry']
		row,col = entry.index(INSERT).split('.')
		row_end,col_end = entry.index(END).split('.')
		
		# check backspace
		if int(col) < 2 and event.keycode == BACKSPACE:
			entry.insert(row+'.'+col,'>')
		# check typing to early
		if int(col) <= 2:
			entry.mark_set(INSERT,row+'.3')
		# check typing to early
		if int(row_end) != int(row):
			entry.mark_set(INSERT,row_end+'.3')
			
if __name__ == '__main__':
	import tkinter as tk
	root = tk.Tk()
	term = LilacTerminal(root,None)
	root.mainloop()
	