"""
	This class extends the grid to provide image support
	
	Author: Matthew Levine
	Date: 12/12/2014
"""
from LiEmmitor.Grid import Grid

import tkinter as tk
from PIL import Image, ImageTk

class ImageGrid(Grid,tk.Canvas):

	def __init__( self, width=500, height=500 ):	
		tk.Canvas.__init__(self,width=width,height=height)
		Grid.__init__( self, width=width, height=height )
		
		self.interupt = False # can be set to stop scheduled events

	def update_idletasks( self ):
		temp = self.view_temperature()
		(w,h) = (self.width,self.height)
		self.image =  Image.frombuffer('RGBA',(w,h),temp,'raw','RGBA',0,1).convert('RGB')
		self.imTk = ImageTk.PhotoImage(self.image.rotate(90))
		self.create_image(w/2,h/2,image=self.imTk)
		
	def schedule( self, time, event, recurring = False ):
		""" Schedules an event to be requested to occur after a certain amount
			of time. This is non-threaded and occurs as available in the queue.
			
			If recurring is true, reschedules this event to occur again on a timer
		"""
		if not recurring: 
			self.mster.after( time, event )
		else: 
			def decorated_event():
				if self.interupt: return
				event()
				self.master.after(time,decorated_event)
			decorated_event()

	
	
if __name__ == '__main__':
	root = tk.Tk()
	
	grid = ImageGrid(root)
	grid.pack()
	for i in range(100,200): 
		for j in range(100,200):
			grid[i,j] = 40000
	grid.update_idletasks()
	
	for i in range(100):
		grid[3,3] = grid[150,150] + 1000000
		grid(150,150,grid(150,150)+100000)
		xpos = grid(150,150)
		print(xpos)
		grid.update_idletasks()
	
	cool = lambda : [grid.step(),grid.update_idletasks(),print('stepping')]
	
	grid.schedule( 100, cool, 1 )
	
	root.mainloop()