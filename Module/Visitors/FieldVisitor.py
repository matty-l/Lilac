"""
	This file contains a visitor that retrieves information from a Module
	Element.
	
	Author: Matthew Levine
	Date: 09/23/2014
"""
from Module.ClassUtils import Overrides
from Module.Visitors.Visitor import Visitor
from Module.Visitors.SphereUpdateVisitor import SphereUpdateVisitor
import tkinter.ttk as tk
from tkinter import StringVar, IntVar
from numpy import mean as npmean, around as npround, array as nparray
from math import sin,cos,pi

from tkinter.filedialog import askopenfilename
from scipy import misc

SC = 1

def set_local_scale( amount ):
	global SC
	SC = amount

class FieldVisitor(Visitor):
		
	def get_element_info(self,window,element):
		""" Retrieves the fields from the given element """
		self.window = window
		self.root = element # just for udpate calls
		self.fields = []
		element.accept(self)		
		
	@Overrides(Visitor)
	def visit_polygon(self,polygon):
		""" Adds the fields to edit a polygon's basic qualities, like position """
		
		# grab the coordinates from the polygon
		coords = polygon.coordinates
		# back up its coordinates, if they are not already backed up
		try: polygon.pure_coordinates
		except: polygon.pure_coordinates = polygon.coordinates.copy()
		
		# define their center as their mean along each axis
		mcoords = npround(npmean(coords,0),0)
		
		coordview = tk.Label(self.window,text='Origin')
		coord_setter = tk.Frame(self.window)
		text_vars = tuple(StringVar() for i in range(4))
		
		# loops don't create new scopes but methods do
		# also it's pretty cool that i gets implied by the loop variable
		def add_entry(event=None): 
			""" Adds an entry field to modify a given axis """
			textVar = text_vars[i]
			textVar.set(str(mcoords[i]))
			e = tk.Entry(coord_setter,textvariable=textVar,width=12)
			e.grid(column=i,row=0)				
			def shift_poly(event = None):
				""" Applies the transformation to shift the polygon, does not redraw canvas """
				try: # it could be that they entered a non-float
					dx = tuple(mcoords[j] - float(text_vars[j].get()) for j in range(4))
				except Exception as e: # in which case, just ignore it
					dx = 0
				# shift each coordinate by the displacement implied by the entry field
				coords = [ [el + dx[j] for j,el in \
						enumerate(coord)] for coord in polygon.pure_coordinates]
				# update the polygon's coordinates (it expects a numpy object)
				polygon.coordinates = nparray(coords)
				polygon._dirty()
			
			# bind to the entry field update-on-entry
			e.bind('<Return>', shift_poly  )
			
		# add all four entry widgets to update 3 axes plus homogeneous	
		for i in range(4): add_entry(i)
		
		self.fields.append(coordview)
		self.fields.append(coord_setter)

	
	@Overrides(Visitor)
	def visit_module(self,module):
		""" Adds the fields to edit a module's qualities, like color, position,
			and rotation
		"""
		ds = module.__elements__[0]
		transform = module.__elements__[1]
		
		self.fields.append(tk.Label(self.window,text='Color'))
		self.__color_mod(ds)
		
		self.fields.append(tk.Label(self.window,text='Rotation'))
		# Add the rotation buttons
		(csx,csy) = (cos(pi/50),sin(pi/50))
		(ssx,ssy) = (cos(-pi/50),sin(-pi/50)) # I don't feel like doing trig
		self.__move_mod(transform,
			func_list = {0:lambda:transform.rotateX(csx,csy),
						1:lambda:transform.rotateY(csx,csy),
						2:lambda:transform.rotateZ(csx,csy) },
			rfunc_list = {0:lambda:transform.rotateX(ssx,ssy),
						1:lambda:transform.rotateY(ssx,ssy),
						2:lambda:transform.rotateZ(ssx,ssy) })
		

		self.fields.append(tk.Label(self.window,text='Translation'))		
		# Add the translation buttons		
		self.__move_mod(transform,
			func_list = {0:lambda:transform.translate(1,0,0),
						1:lambda:transform.translate(0,1,0),
						2:lambda:transform.translate(0,0,1) },
			rfunc_list = {0:lambda:transform.translate(-1,0,0),
						1:lambda:transform.translate(0,-1,0),
						2:lambda:transform.translate(0,0,-1) })	

		self.fields.append(tk.Label(self.window,text='Scale'))		
		# Add the scale buttons		
		self.__move_mod(transform,
			func_list = {0:lambda:transform.scale(2*SC,1,1),
						1:lambda:transform.scale(1,2*SC,1),
						2:lambda:transform.scale(1,1,2*SC) },
			rfunc_list = {0:lambda:transform.scale(.5/SC,1,1),
						1:lambda:transform.scale(1,.5/SC,1),
						2:lambda:transform.scale(1,1,.5/SC) })								
		
		self.fields.append(tk.Button(self.window,text='Enhance',
			command=lambda : SphereUpdateVisitor().update_spheres(self.root) ))
		frame = tk.Frame(self.window)
		self.fields.append(frame)
		var = IntVar()
		var.set(module.ignore*1)
		tk.Checkbutton(frame,text='Ignore',variable=var,
			command=lambda : module.__setattr__('ignore',not module.ignore)).grid(row=0,column=3)
		
		tk.Button(frame,text='Texturize',command=lambda:tex_obj(module)).grid(row=0,column=0)
		
		sc_entry = tk.Entry(frame,width=10)
		sc_entry.insert(0,'Surface')
		sc_entry.bind('<Return>',lambda e:(ds.__setitem__('surface_color',
			[float(x) for x in sc_entry.get().split(' ')]+[1]),
			self.window.update_idletasks(),ds._dirty()))
		sc_entry.grid(row=0,column=2)
		
		tk.Button(frame,text='Bump',command=lambda:bump_obj(module)).grid(row=0,column=1)

	def __color_mod( self, ds ):
		try:
			col = ds['base_color']
			color_setter = tk.Frame(self.window)
			text_vars = tuple(StringVar() for i in range(5))
			
			def add_entry(): 
				""" Adds an entry field to modify a given axis """
				# try: # for rainbow
				textVar = text_vars[i]
				if i < 4: textVar.set(str(col[i]))
				# except IndexError:
					# return	

				else: 
					try:
						textVar.set(str(int(ds['beta'][0]*255)))
					except: # for archaic loads
						ds['beta'] = [1]
						textVar.set(str(int(ds['beta'][0]*255)))						
						
				e = tk.Entry(color_setter,textvariable=textVar,width=7,)
				e.grid(column=i,row=0)			
				
				def shift_color(event = None):
					""" Applies the transformation to change the ds color """
					try: # it could be that they entered a non-float
						new_color = tuple(int(text_vars[j].get()) for j in range(4))
					except Exception as e: # in which case, just ignore it
						new_color = col				
					ds['base_color'] = new_color	
					ds['alpha'] = [1-new_color[3]/255]
					ds['beta'] = [(int(text_vars[4].get()))/255]
					ds._dirty()
					
				
				# bind to the entry field update-on-entry
				e.bind('<Return>', shift_color  )
				
			# add all four entry widgets to update 3 axes plus homogeneous	
			for i in range(5): add_entry()			
			self.fields.append(color_setter)
		except Exception as e:
			raise e
			self.fields.append(tk.Label(self.window,text='No Color'),width=5)
	
		
	def __move_mod( self, transform, func_list, rfunc_list = None ):
		""" Subroutine for adding module fields to the gui """
		try:
			transform_setter = tk.Frame(self.window)
			buttons = tuple((tk.Button(transform_setter) for i in range(3)))
			def move_mod():
				""" Initializes a button to rotate the module based on the
					index, "i", currently in the function scope (for use in loop)
				"""
				# Get the right label, based on the index 
				dir = {0:'x',1:'y',2:'z'}[i]
				# get the right transformation function, based on the index
				func = func_list[i]
				buttons[i].config(text=dir.upper())
				buttons[i].config(command=lambda:(func(),transform._dirty()))
				if rfunc_list is not None:
					rfunc = rfunc_list[i]
					buttons[i].bind('<Button-3>',lambda e:(rfunc(),transform._dirty()))
				buttons[i].grid(row=0,column=i)				
			
			# add all three buttons and configure them
			for i in range(3): move_mod() 
			self.fields.append(transform_setter)
		except AttributeError:
			self.fields.append(tk.Label(self.window,text="No Transform"))			
		
	@Overrides(Visitor)
	def visit_matrix(self,matrix):
		pass
		
def tex_obj(module):
	try:
		file = askopenfilename()
	except Exception as e:
		log = open("log.txt","a")
		log.write("\n"+str(e))
		log.close()
		raise e
		return # file errors are okay

	try:
		tex = misc.imread(file)
		shape = tex.shape if len(tex.shape) == 3 else tuple(list(tex.shape)+[1])
		module.__elements__[0]['texture'] = (tex.flatten().astype(int),shape)
	except Exception as e:
		log = open("log.txt","a")
		log.write("\n"+str(e))
		log.close()		
		raise e
		return # if it isn't an image, that's okay too

def bump_obj(module):
	try:
		file = askopenfilename()
	except Exception as e:
		log = open("log.txt","a")
		log.write("\n"+str(e))
		log.close()
		raise e
		return # file errors are okay

	try:
		tex = misc.imread(file)
		shape = tex.shape if len(tex.shape) == 3 else tuple(list(tex.shape)+[1])
		module.__elements__[0]['bumpmap'] = (tex.flatten().astype(int),shape)
	except Exception as e:
		log = open("log.txt","a")
		log.write("\n"+str(e))
		log.close()		
		raise e
		return # if it isn't an image, that's okay too
