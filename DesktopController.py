"""
	A GUI application using LilacTk
	
	Author: Matthew Levine
	Date: 09/18/2014
"""

import LilacTk as ltk
import tkinter as tk
from Module.Objects.ObjReader import open_obj
from Module.Lighting.Lighting import Lighting
from Module.Module import Module
from Module.IOC import ioc

from Module.Widgets.Terminal import LilacTerminal
from Module.Widgets.ModuleTableView import ModuleViewTable
from Module.Widgets.ToolBar import ToolBar
from Module.Widgets.LilacBinder import LilacBinder
from Module.Widgets.LightController import LightControllerUI

from Module.Matrices.Vector import ModuleVector as Vec

from tkinter.ttk import Notebook, Style, Checkbutton
from tkinter.font import Font
from datetime import datetime, timezone


ioc(globals()) # mark ourselves for dependency injection

class DesktopController:

	def __init__( self ):
		canvas = ltk.LTk()
		self.dir = {
			'canvas' : canvas, # the Ltk root
			'root' : canvas.config('root'), # the Tk Root
			'scene' : canvas.config('modules')[0], # the top-level module
			'scene_index' : 0
		}
		
		self.init_log()
		self.init_style()
		self.init_top_bar()
		self.init_scene()
		
		self.init_right_frame()
		self.init_bindings()
		self.init_menus()

		# for debugging
		# pfile = open('Module/Objects/reflection_simple_test.p','rb')
		# obj = pickle.load(pfile)
		# pfile.close()
		# canvas.config('modules')[0].__elements__ = obj.__elements__
		# canvas.update_idletasks()

		self.dir['root'].attributes('-fullscreen', True)
		canvas.mainloop()
		self.finalize_log()
				
	
	def init_style( self ):
		""" Initializes style for the window """
		self.dir['root'].title('Lilac Modeling Suite')
		self.dir['canvas'].update_idletasks()
		style = Style()
		style.theme_use('clam')
		
	def init_scene( self ):
		""" Initializes lighting on the scene. Adds a point light with a blue
			tint and an ambient white light.
		"""		
		can = self.dir['canvas']
		
		self.move_camera(update=0)
		can.move_camera = self.move_camera # a little dynamic access for the terminal
		
		self.dir['scene'].body_color([255,255,255,255])
		self.dir['scene'].scale(.1,.1,.1)
		self.dir['scene'].id[0] = 'Scene 0'
		

				
		# self.dir['root'].bind('<Key-b>',setbg)
		
	def init_top_bar( self ):
		""" Initializes the top frame """
		bar = tk.Frame( self.dir['root'], height = 1 )
		bar.grid(row=0,columnspan=3,sticky='ew')
		bar.widget = bar.label = None
		# Some utility functions for assigning widgets into the bar
		def assign_to_bar(widget=None,label=''):
			bar.config(height=20)
			if bar.widget is not None: bar.widget.grid_forget()
			widget.grid(row=0,column=0,sticky='ew')
			bar.label = label
			bar.widget = widget
			return bar
		def hide_bar():
			if bar.widget is not None: bar.widget.grid_forget()
			bar.config(height=1)
			bar.label = None
			bar.widget = None
		self.dir['top_bar'] = bar

		bar.is_bar_label = lambda id : bar.label == id
		(bar.assign_to_bar,bar.hide_bar) = (assign_to_bar,hide_bar)
		
	def init_right_frame( self ):
		""" Initializes bottom frame """
		self.dir['frames'] = {'bottom': Notebook( self.dir['root'], width = 500,
			height = 650 ) }
		self.dir['frames']['bottom'].grid(column=2,row=1)
		self.__init_tab2(self.dir['frames']['bottom'])	
		self.__init_tab1(self.dir['frames']['bottom'])	
		self.__init_tab3(self.dir['frames']['bottom'])			
		
	def init_bindings( self ):
		""" Initializes externally managed bindings on the main canvas """
		self.dir['binding_manager'] = LilacBinder()
		self.dir['binding_manager'].init_all_bindings(self.dir['canvas'])
		
	def init_menus( self ):
		""" Initilaizes the menus on the controller """
		main_menu = tk.Menu(self.dir['root'])
		labels = ['File','Scene','Lighting']
		menus = [tk.Menu(main_menu,tearoff=0) for label in labels]
		
		[main_menu.add_cascade(label=label,
			menu=menu) for label,menu in zip(labels,menus)]
			
		menu_opts = [ [
			   ("Save",self.dir['canvas'].save_next_frame),
			   ("Export",lambda:0),
			   ("Load",lambda:0),
			   ("Exit",self.dir['root'].destroy)],
			  [("Change Background",self.__change_bg),
			   ("Clear Layer",self.reset_scene),
			   ("Next Layer",self.next_layer),
			   ("Previous Layer",self.previous_layer),
			   ('Reset GTM',lambda:self.dir['canvas'].config('GTM').identity())],
			  [("Light Settings",lambda:self.open_light_settings(tk.Toplevel())),
			   ("Profile Light Performance",lambda:0),
			   ("Reflection Meta-Parameters",self.__change_meta_reflect),
			   ("Shadow Meta-Parameters",self.__change_meta_shadow),
			   ("Move Lights",self.move_lights)]
					]
		for menu,menuitems in zip(menus,menu_opts):
			for menuitem in menuitems:
				menu.add_command(label=menuitem[0],command=menuitem[1])
			
		
		self.dir['root'].config(menu=main_menu)
		
	def init_log( self ):
		""" Initializes a very simple text file for writing logs to - no
			output stream is hijacked for this log, it's use is entirely
			optional - the file should be opened and closed as an append-only
			document for logging.
		"""
		log = open("log.py","a")		
		date = datetime.now(timezone.utc).strftime("%Y\\%m\\%d")
		log.write("\n--------------------------\nLilac Session Opened on "+date+"\n")	
		log.close()
				
	def finalize_log( self ):
		""" Adds closing remarks to the log. See init_log for details.
		"""
		log = open("log.py","a")		
		date = datetime.now(timezone.utc).strftime("%Y\\%m\\%d")
		log.write("\nLilac Session Closed Successfully on "+date+"\n--------------------------\n")	
		log.close()
		

	def reset_scene( self ):
		""" In places drops refrences to all elements in the current scene,
			allowing garbage collection to pick them up at its leisure (does
			not force gc). 
			
			Does not guarantee that all references to the 
			elements are dropped - in particular, arbitrary references can
			be created in-terminal, by active native code, or by the module
			list. Refresh the module list manually to remove those references.
			
			References to the actual module are not dropped - the elment
			list witihn the references is dereferenced.			
		"""
		del self.dir['scene'].__elements__[2:]
		self.dir['canvas'].update_idletasks()
		
	def next_layer(self):
		""" Changes the canvas view to the next scene in the queue - 
			creates a new scene if there are no scenes in the queue ahead
			of this one. 
			
			This function does not affect strong references in terms of
			garbage collection.
			
			Temporily, the elements in the root scene will be swapped out;
			these elements are internally preserved
		"""
		modules = self.dir['canvas'].config("modules")
		
		if '__tmp__' in self.dir:		
			modules[0].__elements__ = self.dir['__tmp__']
			
		self.dir['scene_index'] += 1		
		if len(modules) <= self.dir['scene_index']:
			modules.append(Module())
			modules[-1].body_color([255,255,255,255])
			modules[-1].scale(.1,.1,.1)
			modules[-1].id[0] = 'Scene '+str(self.dir['scene_index'])

		self.dir['__tmp__'] = modules[0].__elements__
		modules[0].__elements__ = modules[self.dir['scene_index']].__elements__
		
		self.dir['canvas'].update_idletasks()
		
	def previous_layer(self): 
		""" Changes the canvas view to the previous scene in the queue. Does
			nothing if this is the zero-indexed scene. 
			
			See next_layer for details.
		"""
		if self.dir['scene_index'] <= 0: return
		modules = self.dir['canvas'].config("modules")
		
		if '__tmp__' in self.dir:		
			modules[0].__elements__ = self.dir['__tmp__']
			
		self.dir['scene_index'] -= 1		
		self.dir['__tmp__'] = modules[0].__elements__
		modules[0].__elements__ = modules[self.dir['scene_index']].__elements__
		
		self.dir['canvas'].update_idletasks()
		
	def open_light_settings( self, top, toplevel = 0 ):
		""" Opens a dialog for modifying the light settings """
		L = self.dir['canvas'].config("lighting")
		frame = tk.Frame(top)
		
		vars = [tk.IntVar() for val in range(len(L.settings))]
		[var.set(val) for var,val in zip(vars,L.settings.values())]
		def set(key,val):
			if key == 'texture': 
				self.dir['canvas'].texture = 1-self.dir['canvas'].texture
				L.settings[key] = self.dir['canvas'].texture
			elif key == 'fill': 
				self.dir['canvas'].fill = 1-self.dir['canvas'].fill
				L.settings[key] = self.dir['canvas'].fill
			else: L.settings[key] = 1-L.settings[key]
		
		for i,(key,val) in enumerate(L.settings.items()):				
			choice = Checkbutton(top,text=str(key),variable=vars[i])
			choice.config(command=lambda i=i,
				key=key:set(key,val))
			choice.grid(row=i,column=0,sticky='w')

		if toplevel:
			top.mainloop()
		
	def move_lights( self ):
		""" Opens dialog to move lights in the scene """
		LightControllerUI(self.dir['canvas'],
			tk.Toplevel(),self.dir['canvas'].config("lighting"))
	
	def move_camera( self, config = -1, update = 1 ):
		can = self.dir['canvas']
		can.config('lighting').clear()
		
		if config == 0:
			# head-on configuration 1
			can.create_light([int(0.9*255), int(255*0.85), int(255*0.8),255],Lighting.Point,position=[1.,5,1,1],sharpness=32)
			can.create_light([int(0.4*255), int(0.5*255), int(255*0.6),100],Lighting.Ambient)
			can.set_camera_3D(vrp=Vec(0,4,0), vpn=Vec(0,-1,0), vup=Vec(1,0,1),
				 d = 1, f = 0, b = 4,rows=750,cols=750)
		elif config == 1:
			# head-on configuration 2
			can.create_light([178,178,178,255],Lighting.Point,position=[0,0,-3,1],sharpness=4)
			can.create_light([178,178,178,100],Lighting.Ambient)
			can.set_camera_3D(vrp=Vec(0,0,-3), vpn=Vec(0,1,0), vup=Vec(0,0,1),
				 d = 1, f = 0, b = 4,rows=750,cols=750)
		elif config == 2:
			can.create_light([178,178,178,255],Lighting.Point,position=[3,3,-3,1],sharpness=4)
			can.create_light([178,178,178,100],Lighting.Ambient)
			can.set_camera_3D(vrp=Vec(0,3,-3), vpn=Vec(0,-1,1), vup=Vec(0,1,0),
				 d = 1, f = 0, b = 4,rows=750,cols=750)			
		else:
			# main configuration
			can.create_light([178,178,178,255],Lighting.Point,position=[2,2.,-2,1],sharpness=4)
			can.create_light([178,178,178,255],Lighting.Ambient)
			can.set_camera_3D(rows=750,cols=750)
			
		if update: can.update_idletasks()

	
	
	################################
	## INTERNAL STUFF LIKE LAYOUT ##
	################################
	def __init_tab1( self, book ):
		"""
			Initializes the tab with control buttons.
			
			This function is meant for INTERNAL use only
		"""
		tab = tk.Frame(book)
		book.add(tab,text='Tools')
		
		toolbar = ToolBar( tab, scene=self.dir['canvas'] )
		toolbar.grid()
		
		self.open_light_settings( toolbar.canvas.light_settings )
	
	def __init_tab2( self, book ):
		""" Initializes the tab that has the terminal in it
		
			This function is meant for INTERNAL use only
		"""
		tab = tk.Frame(book)
		book.add(tab,text='Terminal')		
		terminal = LilacTerminal(tab,self.dir['canvas'],height=45)

	def __init_tab3( self, book ):
		""" Initializes the module-view table
			
			This function is meant for INTERNAL use only
		"""
		tab =  tk.Frame(book)
		book.add(tab,text='Modules')
		table = ModuleViewTable(tab,scene=self.dir['scene'])
		table.grid(sticky='nsew')
		
	def __change_bg(self):
		""" Opens dialog to change the background color
		
			This function is meant for INTERNAL use only
		"""
		bar = self.dir['top_bar']
		if bar.is_bar_label('background'): 
			bar.hide_bar()
			return
		pop = tk.Frame(bar)
		can = self.dir['canvas']
		(e1,e2,e3) = (tk.Entry(pop,width=4) for i in range(3))
		[e1.grid(column=0,row=0),e2.grid(column=1,row=0),e3.grid(column=2,row=0)]
		tk.Button(pop,text='Set Background',font=Font(size=8,family='Courier'),
			command=lambda:Lighting.set_bg(\
			int(e1.get()),int(e2.get()),int(e3.get()), can ) ).grid(row=0,column=3)
		bar.assign_to_bar(widget=pop,label='background')

	def __change_meta_reflect(self):
		""" Opens dialog to change the meta-parameters on reflection
			computations. Changes do not have affect unless reflection
			is enabled on the scene
			
			This function is meant for INTERNAL use only
		"""
		bar = self.dir['top_bar']
		if bar.is_bar_label('reflection'): 
			bar.hide_bar()
			return
		pop = tk.Frame(bar)
		can = self.dir['canvas']
		texts = [tk.StringVar() for i in range(6)]
		[t.set(s) for t,s in zip(texts,['Offset','Projection','Diffusion','Threshold','Area X','Area Y'])]
		(e1,e2,e3,e4,e5,e6) = (tk.Entry(pop,width=8,textvariable=texts[i]) for i in range(6))
		[e1.grid(column=0,row=0),e2.grid(column=1,row=0),e3.grid(column=2,row=0),
		e4.grid(column=3,row=0),e5.grid(column=4,row=0),e6.grid(column=5,row=0)]
		tk.Button(pop,text='Set Reflection Options',font=Font(size=8,family='Courier'),
			command=lambda: Lighting.set_reflection_values(float(e1.get()),
			int(e2.get()),int(e3.get()),float(e4.get()),int(e5.get()), int(e6.get()), can ) ).grid(column=6,row=0)
		bar.assign_to_bar(widget=pop,label='reflection')

	def __change_meta_shadow(self):
		""" Opens dialog to change the meta-parameters on shadow-tracing
			computations. Changes do not have affect unless shadow-tracing
			is enabled on the scene
			
			This function is meant for INTERNAL use only
		"""		
		bar = self.dir['top_bar']
		if bar.is_bar_label('shadow'): 
			bar.hide_bar()
			return
		pop = tk.Frame(bar)
		can = self.dir['canvas']
		texts = [tk.StringVar() for i in range(5)]
		[t.set(s) for t,s in zip(texts,['Area X','Area Y','Tolerance','Diffusion','Darkness'])]
		(e1,e2,e3,e4,e5) = (tk.Entry(pop,width=8,textvariable=texts[i]) for i in range(5))
		[e1.grid(column=0,row=0),e2.grid(column=1,row=0),
			e3.grid(column=2,row=0),e4.grid(column=3,row=0),e5.grid(column=4,row=0)]
		tk.Button(pop,text='Set Shadow Options',font=Font(size=8,family='Courier'),
			command=lambda: Lighting.set_shadow_values(\
			int(e1.get()),int(e2.get()),float(e3.get()),int(e4.get()),float(e5.get()), can ) ).grid(column=5,row=0)
		bar.assign_to_bar(widget=pop,label='shadow')
			
if __name__ == '__main__':
	DesktopController()