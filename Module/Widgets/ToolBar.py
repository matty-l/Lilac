"""
	This file contains a Tk-based ToolBar widget for use with a Lilac GUi
	
	Author: Matthew
	Date: 09/24/2014
"""

import tkinter as tk
from tkinter.ttk import Combobox as tkComboBox, Scale
from math import cos,sin,pi
import pickle
from Module.Module import Module
from Module.Shapes.SphereGenerator import SphereGenerator
from Module.Matrices.Vector import ModuleVector as Vec
from Module.Lighting.Lighting import Lighting
from Module.IOC import ioc # mark ourselves for dependency injection
ioc(globals())

# fixme: module vars are sloppy
texture = ['mercury.jpg','jupiter.jpg','mars.jpg', 'pluto.jpg']
tex_index = 0


class ToolBar(tk.Frame):

	def __init__( self, root, scene ):
		""" Initializes the toolbar """
		tk.Frame.__init__( self, root )
		self.canvas = scene
		self.vrp = Vec(3,2,-2)
		self.vpn = Vec(-3,-2,2)
		self.__iter = 0
		self.__build()
		
	def add_title( self, string, row ):
		""" Adds the indicated title to the given row in the manager """
		tk.Label(self, text = '\n'+string,font=('Helvetica',16,
			'bold')).grid(row=row,column=0,sticky='we',columnspan=2)
		
		
	def __build( self ):
		""" Builds the toolbars various features and buttons """
		self.add_title('Animation Control',row=0)
		
		self.__build_start() # the start animation button
		self.__build_stop() # the stop animation button
		self.__build_save() # the save button
		self.__build_inserter() # the button to insert new elements
		self.__build_lightness_slider()
		self.__build_fog_slider()
		self.__build_light_settings()
		
		# this should go in the binder, but breaks my linkage structure and whatever
		def adjust(event): 
			self.vrp *= .9 
			self.canvas.set_camera_3D(vrp=self.vrp,vpn=self.vpn)
			self.canvas.update_idletasks()
		def rejust(event): 
			self.vrp /= .9
			self.canvas.set_camera_3D(vrp=self.vrp,vpn=self.vpn)
			self.canvas.update_idletasks()
		def normup(event):
			self.vpn += [.1,0,0,0]
			self.canvas.set_camera_3D(vrp=self.vrp,vpn=self.vpn)
			self.canvas.update_idletasks()
		def normdw(event):
			self.vpn -= [.1,0,0,0]
			self.canvas.set_camera_3D(vrp=self.vrp,vpn=self.vpn)
			self.canvas.update_idletasks()
		def normlt(event):
			self.vpn += [0,.1,0,0]
			self.canvas.set_camera_3D(vrp=self.vrp,vpn=self.vpn)
			self.canvas.update_idletasks()
		def normrt(event):
			self.vpn -= [0,.1,0,0]
			self.canvas.set_camera_3D(vrp=self.vrp,vpn=self.vpn)
			self.canvas.update_idletasks()
		
		super = self.master.master.master
		# super.bind("<Up>",normup)
		# super.bind("<Down>",normdw)
		# super.bind("<Left>",normlt)
		# super.bind("<Right>",normrt)
		# self.bind("<Button-1>",adjust)
		# self.bind("<Button-3>",rejust)
		
	def __build_stop(self):
		"""Builds the stop animation button """
		def stop(event=None):	
			""" Stops the canvas animation """
			self.canvas.config(interupt=True)
		tk.Button(self,image=self.__stopimage,
			command=stop).grid(row=1,column=1,sticky='w')		
			
	def __build_start(self):
		""" Builds the start-animation button """
		sh =[50]
		def play(event=None):
			"""" Starts the canvas animation """
			self.canvas.config( interupt = False )
			def transform():
				""" Rotates the entire canvas and updates the screen """
				self.canvas.config('GTM').rotateY(cos(.05),sin(.05))
				# for i,el in enumerate(self.canvas.config('modules')[0].__elements__):
					# try:
						# angle = 0.025 * 2
						# el.__elements__[1].rotateY(cos(angle),sin(angle))
					# except Exception as e: pass
					
				# Uncomment to zoom camera
				# self.canvas.set_camera_3D(vrp=self.vrp)
				# self.vrp *= .99
				
				self.canvas.update_idletasks()
				
				# Save the image
				s = ''.join(['0' for i in range(6-\
					len(str(self.__iter)))]+[str(self.__iter)])				
				self.canvas.config('image').save('images/gif_base/image_'+s+'.png','PNG')
				self.__iter += 1
				
			self.canvas.schedule(10,transform,1)
			
		def play_light(event=None):	
			self.canvas.config( interupt = False )
			def transform():
				""" Rotates the entire canvas and updates the screen """
				self.canvas.config('lighting').clear()
				self.canvas.create_light([sh[0],sh[0],sh[0],255],Lighting.Point,position=[0,0,-3,1],sharpness=4)
				self.canvas.create_light([20,20,20,255],Lighting.Ambient)
				sh[0] += 1
				self.canvas.update_idletasks()
				
				# Save the image
				s = ''.join(['0' for i in range(6-\
					len(str(self.__iter)))]+[str(self.__iter)])				
				self.canvas.config('image').save('images/desktop_controller/image_'+s+'.png','PNG')
				self.__iter += 1
				
			self.canvas.schedule(10,transform,1)


		self.__playimage = tk.PhotoImage(file='images/PlayButton.gif')
		self.__stopimage = tk.PhotoImage(file='images/StopButton.gif')
		tk.Button(self,image=self.__playimage,
			command=play).grid(row=1,column=0,sticky='w')		
			
	def __build_save(self):
		""" Builds the save button """
		def save(event=None):
			""" Saves an image of the current canvas """
			s = ''.join(['0' for i in range(6-\
				len(str(self.__iter)))]+[str(self.__iter)])				
			self.canvas.config('image').save('images/desktop_controller/image_'+s+'.png','PNG')
			self.__iter += 1
		def pickleit(event=None):
			""" Saves a pickled version of the current scene """
			s = ''.join(['0' for i in range(6-\
				len(str(self.__iter)))]+[str(self.__iter)])				
			pfile = open('Module/Objects/scene_'+s+'.p','wb')
			pickle.dump(self.canvas.config('modules')[0], pfile, protocol=-1)
			self.__iter += 1
			pfile.close()
		def depickle(event=None):
			""" Loads a pickled version of the given scene """
			pop = tk.Toplevel()
			ent = tk.Entry(pop)
			ent.grid(row=0,column=0)
			def onsubmit(event=None):
				try:
					pfile = open('Module/Objects/'+str(ent.get()),'rb')
					obj = pickle.load(pfile)
					pfile.close()
				except Exception as e:
					print('Exception: ',e)
					pop.destroy()
					raise e
					return
				# self.canvas.config('modules')[0].__elements__ = obj.__elements__
				if len(obj.__elements__) == 3:
					obj = obj.__elements__[-1]
					try: obj.__elements__[-1].__elements__[0] = obj.__elements__[0]
					except:pass
				self.canvas.config('modules')[0].__elements__.append( obj )
					
				self.canvas.update_idletasks()
				pop.destroy()
			tk.Button(pop,command=onsubmit,text='Load').grid(row=0,column=1)
		def replace(event=None):
			""" Loads a pickled version of the given scene """
			pop = tk.Toplevel()
			ent = tk.Entry(pop)
			ent.grid(row=0,column=0)
			def onsubmit(event=None):
				try:
					pfile = open('Module/Objects/'+str(ent.get()),'rb')
					obj = pickle.load(pfile)
					pfile.close()
				except Exception as e:
					print('Exception: ',e)
					pop.destroy()
					raise e
					return
				self.canvas.config('modules')[0].__elements__ = obj.__elements__
				# self.canvas.config('modules')[0].__elements__.append( obj )
				self.canvas.update_idletasks()
				pop.destroy()
			tk.Button(pop,command=onsubmit,text='Load').grid(row=0,column=1)
			
		tk.Button(self,text='S',command=save).grid(row=1,column=2,sticky='w')
		tk.Button(self,text='P',command=pickleit).grid(row=1,column=3,sticky='w')
		tk.Button(self,text='Y',command=depickle).grid(row=1,column=4,sticky='w')
		tk.Button(self,text="'R",command=replace).grid(row=1,column=5,sticky='w')
		replace
			
	def __build_inserter(self):
		""" Builds the module insertion button """
		self.add_title('Object Creator',row=2)
		
		def insert(event=None):
			global tex_index
			module = Module()
			module.body_color([ int(0.7*255), int(0.2*255), int(0.1*255),255])
			module.__elements__[0]['surface_color'] = [.3,.3,.3,1]
			module.scale(16,16,16)
			shape_factory.cache = False
			module.add_element(shape_factory.gen_shape(choice.get()))
			try:
				module.__elements__[-1].__elements__[0] = module.__elements__[0]
			except: pass
			# hacky but we'll fix later
			if module.__elements__[-1].id[0] == 'Sphere':
				# SphereGenerator.texture_sphere(module.__elements__[-1],
					# texture[tex_index])
				tex_index += 1
				if tex_index == len(texture): tex_index = -tex_index
			elif module.__elements__[-1].id[0] == 'Xwing':
				module.__elements__[-2].scale(.02,.02,.02)

			shape_factory.cache = False
			module.__elements__[-1].invisible = True
			module.id[0] = module.__elements__[-1].id[0]

			self.canvas.config('modules')[0].add_element(module)
			self.canvas.update_idletasks()
			
						
		modules = shape_factory.module_names()
		choice = tkComboBox(self,values=modules)
		choice.current(0)
		choice.grid(row=3,column=0)
		
		tk.Button(self,text='Add Object',command=insert).grid(row=3,column=1)
		
	def __build_lightness_slider(self):
		""" Builds a slider that allows the user to adjust light intensity
			on the scene
		"""
		can = self.canvas
		self.add_title('Light Brightness',4)
		
		def adjust(event=None):
			d = 1
			s = int(light_meter.get())
			pos = can.config('lighting').get_lighting_parameters()[2][0]
			can.config('lighting').clear()
			can.create_light([s,s,s,s],Lighting.Point,position=pos,sharpness=4)

			can.create_light([s,s,s,s],Lighting.Ambient)
			textvar.set("Brightness: "+str(s))
			can.update_idletasks()
		
		light_meter = Scale( self, to = 255, from_ = 1, length = 200 )
		light_meter.grid(row=5,column=0)
		textvar = tk.StringVar()
		textvar.set("Brightness: 178")
		tk.Label(self,textvariable=textvar).grid(row=5,column=1)
		light_meter.set(178)
		light_meter.configure(command=adjust)
		
	def __build_fog_slider(self):
		""" Builds a slider that allows the user to adjust light intensity
			on the scene
		"""
		can = self.canvas
		self.add_title('Fog Scalar',6)
		
		def adjust(event=None):
			d = 1
			s = int(fog_meter.get())
			can.config('lighting').set_fog_scale(s)
			if s > 0 and s != 70:
				textvar.set("Fog Magnitude: "+str(s))
			elif s == 70:
				textvar.set("Fog Magnitude: :)")
			else:
				textvar.set("Fog Magnitude: OFF")
			can.update_idletasks()
		
		fog_meter = Scale( self, to = 120, from_ = 0, length = 200 )
		fog_meter.grid(row=7,column=0)
		textvar = tk.StringVar()
		textvar.set("Darkness: 0")
		tk.Label(self,textvariable=textvar).grid(row=7,column=1)
		fog_meter.set(0)
		fog_meter.configure(command=adjust)
		
	def __build_light_settings(self):
		""" Builds a frame and saves it as a field, to be populated by
			the DesktopController with lighting choice modifiers. This
			creates an iritating dependency, but is chosen for simplicity
			over elegance.
		"""
		can = self.canvas
		self.add_title('Light Settings',8)
		can.light_settings = tk.Frame( self, relief = tk.SUNKEN, width=400,
			height=400, borderwidth=3 )
		can.light_settings.grid(row=9,column=0,sticky='nsew')
