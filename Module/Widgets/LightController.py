"""
	This file contains basic interface support for moving light
	sources in the scene.
	
	Author: Matthew Levine
	Date: 11/13/2014
"""

import tkinter as tk
import tkinter.ttk as ttk

class LightControllerUI(tk.Frame):
	""" This class provides basic UI support for moving and adding
		light sources to a scene
	"""

	def __init__(self, ltk, root, lighting):
		""" Instantiates a new LCUI within a root widget
		"""
		tk.Frame.__init__(self,root)
		self.L = lighting
		self.ltk = ltk
		self.state = lighting.get_lighting_parameters()[2][0].tolist()#(3,2,-2,1)
		self.sharpness = 4
		self.build_controls()
		self.grid()
		
	def build_controls(self):
		""" Builds controls into the UI """
		#text = ["<",">","IN","UP","DW","OUT",Sharp,Desharp,null]
		text = [chr(8672),chr(8674),chr(10164),chr(8673),chr(8675),chr(10166),'+','-','O']
		self.buttons = [ttk.Button(self,text=text[i]) for i in range(9)]
		[b.grid(row=1+i%3,column=i//3) for i,b in enumerate(self.buttons)]
		dirs = [(.1,0,0),(-.1,0,0),(0,0,.1),(0,.1,0),(0,-.1,0),(0,0,-.1),(None,1),(None,-1),(None,0)]
		[b.config(command=lambda d=dirs[i]:self.move(d)) for i,b in enumerate(self.buttons)]
		self.text = tk.Label(self)
		self.__update_text()
		self.text.grid(row=0,column=0,columnspan=3)
		
		ent = [tk.Entry(self,width=10) for i in range(3)]
		[(  e.grid(column=i,row=4,sticky='ew'),
			e.bind("<Return>",lambda ev,i=i,k=e: (self.state.__setitem__(i, float(k.get()))
			,self.__update_text() ))) for i,e in enumerate(ent)]
		
		
	def move( self, d ):
		""" Moves the light source by the given direction """
		if d[0] is not None:
			self.state = [self.state[0]+d[0],self.state[1]+d[1],self.state[2]+d[2],1]
		else:
			print(self.sharpness)
			self.sharpness += d[1]
		s = list(self.state)
		
		(lights,_,__,sh) = self.L.get_lighting_parameters()
		self.L.clear()

		self.L.add_light(lights[0].tolist(),2,position=s,sharpness=self.sharpness)
		self.L.add_light(lights[1].tolist(),1,sharpness=self.sharpness)
		self.ltk.update_idletasks()
		self.__update_text()
		
	def __update_text(self):
		self.text.config(text="Light Position: "+str(self.state)+"  Sharpness: "+str(self.sharpness))