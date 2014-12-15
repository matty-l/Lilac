"""
	This file contains a Python/C Graphics package with Tkinter interfacing 
	with Tcl/Tk.
	
	The interface attempts to follow Tkinter syntax as much as possible without
	introducing significant inconvenience.
	
	All shapes on modules added are also returned; they can be modified locally,
	or the scene can be changed by modifying the GTM/VTM, or by switching cameras.
	
	The interface redraws itself using an estimation method of determining
	when it is "dirty", based on the likewise dirtiness of the recursively
	descending elements in its primary scene module.
	
	include __future__ (Notes on soon-to-be features)
			
	- Have program make you breakfast (still a ways away)
	
	Author: Matthew Levine
	Date: 09/04/2014 - Created
"""

# External dependency imports
import numpy as np
import tkinter as tk # Just use Python 3
from PIL import Image, ImageTk

# Basic imports
import signal
import time

# package imports
from Module.Module import Module
from Module.ModuleList import ModuleList as mlist

from Module.Matrices.Matrix import ViewTransformationMatrix, IdentityMatrix
from Module.Matrices.View2D import View2D
from Module.Matrices.View3D import View3D

from Module.Lighting.DrawState import DrawState as DS
from Module.Lighting.Lighting import Lighting

from Module.Visitors.FlipVisitor import FlipVisitor

class LTk:
	""" This class is a Tk agent for doing cool graphics """
		
	def __init__( self, **options ):
		""" Initializes a new LilacTk Window.
			
			Some fields, like width and height, are "suggested." This is because Tkinter managers will
			sometimes do whatever they please when placing widgets in a root or parent widget. Regardless,
			the drawing agents try to obey your wishes when given dimensions. This will only be violated
			when the limits cause error. We assume valid input in all cases.
			
			Options that are not valid keys will simply be ignored, ttk style.
			
			Cygwin requires you to SSH - Lilac requires Cygwin. This is because you can't build C extensions
			to Python on Windows in any reasonable way within using Cygwin. Actually, Cygwin isn't reasonable
			either, it's a monster, but still. Once in Cygwin, it requires creating an XWin server in order
			to launch anything tcl. Once in Xwin, all calls must be made manually to the canvas; normal TK
			update calls either do not occur, or are not recorded.
			
			The widgets here-within use the grid manager by default. This may cause problems (including serious
			freezing) if widgets are provided to the agent that are managed using pack, place, etc. Let this
			class do all your managing, if you're using it at all, is the unbiased recommendation.
					
			Options:
				- root : a Tkinter parent window or widget
				- width : the suggested width of the widget
				- height : the suggested height of the widget
				- pixels : the data array (must be a flat contiguous numpy array)
				- update: whether to automatically refresh the canvas
				- background : the background color (in hex)
		
		"""
		self.__opts = {}
		# We use lambda because we don't want to create an unnessary Tkinter window or widget if given
		defaults = { 'root' : lambda:tk.Tk(), 'width' : lambda:750, 'height' : lambda:750, 
					'bg' : lambda:'white', 'modules' : lambda : mlist([Module()]),
					'update' : lambda:True, 'redraws':lambda:False,
					'fps' : lambda:0, 'start_time' : lambda : time.time(),
					'background' : lambda : 0xFFFFFF, 'interupt' : lambda:False,
					'frame_number': lambda : 0, 'selective_shadows' : lambda:False}
		# For every key in the defaults, use yours if provided otherwise mine
		self.__opts = { key : options[key] if key in options else defaults[key]() for key in defaults.keys() }
		
		self.__init_widgets() # Initialize widgets
		self.__init_image() # Initialize image
		self.__init_draw_space() # Initialize the dictionary of drawing information
		self.__auto_refresh() # set auto refresh
		
		
	# -- EXTERNAL FUNCTIONS -- #
				
	def config( self, *queries, **new_options ):
		"""
			If given one argument, returns the value of that argument. If given keyword arguments,
			sets those options. Throws an exception if the options don't exist. See the constructor
			for available options.
			
			Note that the options are set iteratively; just because it fails on one options, doesn't
			mean it failed to set the previous options; since the options are in a dictionary, there
			is not guarantee that the order you input them is the order they are iterated. Thus,
			it is not a good idea to use this function in a try/catch to see if an option exists.
		"""
		if len(queries) > 1:	
			return (self.__opts[query] for query in queries)
		elif len(queries) > 0:
			return self.__opts[queries[0]]
		for opt_name,new_opt in new_options.items():
			self.__opts[opt_name] = new_opt
			
	def mainloop( self ):
		""" Enters a mainloop on the root widget """
		self.__opts['root'].mainloop()
		
	def destroy( self ):
		""" Kills the interface """
		self.__opts['root'].destroy()
		
	def create_point( self, x0, y0, radii = 10, color = (0,0,0,0), id=0   ):
		""" Creates a flat circle at the indicated position 
			Parameters:
			- x0 : the starting x position of the oval
			- y0 : the starting y position of the oval
			
			Optional Parameters
			- radii : the radius of the oval
			- color : three tuple of r g b values
			- id : the identifier of the parent module			
		"""
		return self.__opts['modules'][id].add_shape(shape_factory.gen_shape( 'point',
											x=x0,y=y0,radii=radii,color=color ))

	def create_point_cloud( self, coordinates, color, radii = 10, id=0   ):
		""" Creates a flat circle at the indicated position 
			Parameters:
			- coords : the coordiantes of the points
			- colors : the colors of the points
			
			Optional Parameters
			- radii : the radius of the oval
			- id : the identifier of the parent module			
		"""
		return self.__opts['modules'][id].add_shape(shape_factory.gen_shape( 'pointcloud',
				coords=coordinates,radii=radii,color=color ))
											
	def create_line( self, x0, y0, x1, y1, color = (100,0,0), z0 = 0, z1 = 0,id=0 ):
		""" Creates a line at the indicated position 
			Parameters:
			- x0 : the starting x position of the line
			- y0 : the starting y position of the line
			- x1 : the ending x position of the line
			- y1 : the ending y position of the line			
			
			Optional Parameters
			- color : a three tuple of r g b values
			- z0 : the starting z position
			- z1 : the ending z position
			- id : the identifier of the parent module			
		"""
		return self.__opts['modules'][id].add_shape(shape_factory.gen_shape('line',
			coords=np.array([[x0,y0,z0],[x1,y1,z1]]),color=np.array(color)))
			
	def create_polyline( self, start_coords, end_coords, 
										color = np.array([100,0,0,0]), id=0 ):
		""" Creates the lines at the indicated positions
			Parameters:
			- start_coords : numpy array of starting coordinates
			- end_coords : numpy array of ending coordinates
			
			Optional Parameters
			- color : list of four tuples of r g b a values
			- id : the identifier of the parent module			
		"""
		return self.__opts['modules'][id].add_shape(shape_factory.gen_shape('polyline',
			starts=start_coords, ends=end_coords, color=color))
			
	def create_polygon( self, coords, color = [100,0,0,0],id=0 ):
		""" Creates the polygon at the indicated position
			Parameters:
			- coords : numpy array of coordinates
			
			Optional Parameters
			- color : list of r g b a values
			- id : the identifier of the parent module			
		"""
		return self.__opts['modules'][id].add_shape(shape_factory.gen_shape('polygon',
			coords=coords, color=color))
			
	def create_rectangle( self, x0, y0, width, height, color = [100,0,0,0],id=0):
		""" Creates a rectangle at the indicated position
			Parameters:
			- x0 the x position of the origin of the rectangle
			- y0 the y position of the origin of the rectangle
			- width the width of the rectangle
			- height the height of the rectangle
			
			Optional Parameters
			- color : r g b a values for the rectangle
			- id : the identifier of the parent module			
		"""
		return self.__opts['modules'][id].add_shape(shape_factory.gen_shape('rectangle',
			x0=x0,y0=y0,width=width, height=height, color=color))
			
	def create_cylinder( self, x0, y0, width, height, color=[100,0,0,0], id=0, sides=10 ):
		""" Creates a cylinder at the indicated position
			Parameters:
			- x0 the x position of the origin of the cylinder
			- y0 the y position of the origin of the cylinder
			- width the width of the cylinder
			- height the height of the cylinder
			
			Optional Parameters
			- color : r g b a values for the cylinder
			- id : the identifier of the parent module
			- sides : the number of sides to use in drawing the cylinder
		"""
		return self.__opts['modules'][id].add_element(shape_factory.gen_shape('cylinder',
			x0=x0,y0=y0,width=width, height=height, color=color, sides=sides))

	def create_box( self, x0, y0, z0, width, height, depth, 
					color = [[100,0,0,0] for i in range(6)], id=0 ):
		""" Creates a box at the indicated position
			Parameters:
			- x0 the x position of the origin of the box
			- y0 the y position of the origin of the box
			- z0 the z position of the origin of the box
			- width the width of the box
			- height the height of the box
			- depth the depth of the box
			
			Optional Parameters
			- color : r g b a values for the sides of the rectangle
			- id : the identifier of the parent module
		"""
		return self.__opts['modules'][id].add_element(shape_factory.gen_shape('box',
			x0=x0, y0=y0, z0=z0, width=width, depth=depth, height=height, 
			color=color))
			
	def create_module( self, parent_id = 0 ):
		""" Adds a module to the interface as a sub-module of
			of the module of the given id.
		"""
		mod = Module()
		self.__opts['modules'].append(mod)
		mod.index = len(self.__opts['modules']) - 1
		return self.__opts['modules'][parent_id].add_element(mod)
			
	def create_rotation( self, cth, sth, rotation,id=0 ):
		""" Adds the given transformation to the scene.
			Parameters:
			cth : the cosine of the angle of the transformtion
			sth : the sine of the angle of the transformation
			rotation : the axis of rotation, either x, y, or z
			
			Optional Paramteres:
			- id : the identifier of the parent module
		"""
		Mtx = ViewTransformationMatrix
		m = Mtx()
		{'x':Mtx.rotateX,'y':Mtx.rotateY,'z':Mtx.rotateZ}[rotation](m,cth,sth)
		return self.__opts['modules'][id].add_element(m)
		
	def create_identity( self, id=0 ):
		""" Adds a matrix to the scene which triggers a reset to the 
			local transformation matrix, when struck
			
			Optional Parameters:
			- id : the identifier of the parent module			
		"""
		return self.__opts['modules'][id].add_element(IdentityMatrix())
	
	def create_body_color( self, color, id = 0 ):
		""" Adds a new color change to the pipelien
			Parameters:
			- color : the new color to add
			Optional Parameters:
			- id : the identifier of the parent module			
		"""
		self.__opts['modules'][id].body_color(color)
		
	def create_light( self, color, light_type, position = [0,0,0,1], sharpness=4 ):
		"""
			Creates a new lighting source on the scene
			Parameters:
			- color : the r g b a values of the light
			- light_type: the type of light used
			
			Optional Parameters:
			- position : the position of the light
			- sharpness : the sharpness of the light
		"""
		self.__opts['lighting'].add_light( color, light_type, position = position,
			sharpness = sharpness)
			
	def set_auto_update( self, flag ):
		""" Toggles whether to automatically redraw the canvas when possible """
		if flag and not self.__opts['update']:
			self.__auto_refresh()
		self.__opts['update'] = flag			
			
	def update_idletasks( self ):
		""" Redraws the canvas with the current projection.
			
			The canvas is automatically updated; this function forces the
			procedure at a particular interval.
		"""
		(can,width,height,gtm,vtm,ds,bg,lighting) = \
			self.config('canvas','width','height','GTM',
				'camera','ds','background','lighting')
		can.delete('all') # clear the canvas
		
		t0 = time.time()
		self.__opts['pixels'] = np.ones((width,height),np.uint32) * bg
		from random import randint
		for i in range(200): self.__opts['pixels'][randint(0,700),randint(0,700)] = 0xFFFFFF

		self.__opts['zbuffer'] = np.ones((width,height),np.float32) * 1e3;
		pix = self.__opts['pixels']
		self.__opts['lighting'].reset_trace_buffer()
		
		# Update the canvas with our module
		self.__opts['modules'][0].draw_to_image( self, draw_state = ds,
			view_transformation_matrix = vtm, global_transformation_matrix=gtm,
			lighting=lighting)
		# Apply shadows, reflections, transparency 
		self.__apply_shadows()

		# Toggle shadowed/un-shadowed elements
		if self.__opts['selective_shadows']:
			FlipVisitor().flip_all(self.__opts['modules'][0])
			self.__opts['modules'][0].draw_to_image( self, draw_state = ds,
				view_transformation_matrix = vtm, global_transformation_matrix=gtm,
				lighting=lighting)
			FlipVisitor().flip_all(self.__opts['modules'][0])
		
		self.__opts['modules'][0]._clean()
		
		# redraw the canvas
		self.__opts['image'] = Image.frombuffer('RGBA',(width,height),
			pix,'raw','RGBA',0,1).convert("RGB")
		self.__opts['photo_image'] = ImageTk.PhotoImage(self.__opts['image'])
		can.create_image(width/2,height/2-20,image=self.__opts['photo_image'])
		self.__opts['redraws'] += 1
		self.__opts['fps'] = int(60 / (time.time() - t0))
	
	def force_redraw( self ):
		""" Forces the canvas to immediately redrwa without changing
			the pixels
		"""
		
		(width,height,pix,can) = self.config('width','height','pixels','canvas')
		can.delete('all')
		self.__opts['image'] = Image.frombuffer('RGBA',(width,height),
			pix,'raw','RGBA',0,1).convert("RGB")
		self.__opts['photo_image'] = ImageTk.PhotoImage(self.__opts['image'])
		can.create_image(width/2,height/2-20,image=self.__opts['photo_image'])
		self.__opts['redraws'] += 1
	
	def schedule( self, time, event, recurring = False ):
		""" Schedules an event to be requested to occur after a certain amount
			of time. This is non-threaded and occurs as available in the queue.
			
			If recurring is true, reschedules this event to occur again on a timer
		"""
		if not recurring: 
			self.__opts['root'].after( time, event )
		else: 
			def decorated_event():
				if self.__opts['interupt']: return
				event()
				self.__opts['root'].after(time,decorated_event)
			decorated_event()
				
		
		
	def wait_for_mouse( self, on_continue ):
		""" Idles the thread until a mouse event occurs on the canvas.
			When the event occurs, on_continue is fired with no arguments.
		"""
		self.__opts['canvas'].bind("<Button-1>", lambda e : on_continue() )
	
	def set_camera_2D( self ):
		""" Sets the interface to use a 2D camera (the default mode) """
		self.__opts['camera'] = View2D().setView2D()
		
	def set_camera_3D( self, **kwargs ):
		""" Sets the interface to use a 3D camera """
		self.__opts['camera'] = View3D(**kwargs).setView3D()
		
	def save_next_frame( self, filename = 'animation' ):
		""" Saves the image as an animation identified by a unique frame
			number for the current program execution
		"""
		image, i = self.config('image','frame_number')
		s = ''.join(['0' for j in range(6-len(str(i)))]+[str(i)])
		image.save('images/gif_base/'+filename+'_'+s+'.png','PNG')
		self.config(frame_number = (i+1))

	
	###################################
	# -- INTERNAL BORING FUNCTIONS -- #
	# --     Modify at own peril   -- #
	###################################
	
	def __init_widgets(self):
		""" Initializes widgets """
		# Build the canvas
		(root,width,height,bg) = (self.__opts['root'], self.__opts['width'], 
									self.__opts['height'],self.__opts['bg'])
		self.__opts['canvas'] = tk.Canvas(root,width=width,height=height,bg=bg,
			relief='sunken',highlightbackground='black')
		self.__opts['canvas'].grid(row=1,column=0)
		# Set the tile (Uber important)
		root.title("Lilac")
				
	def __init_image( self ):
		""" Initializes the image drawn on the canvas 
			
			There's a lot of hashing going on in this function that could be
			eliminated by a few more lines of code, like the ones in this comment.
			
			This is an internal function called at instantiation.
		"""
		# Create a pixel array to store our data
		(width,height,bg) = self.config('width','height','background')
		pixels = self.__opts['pixels'] = np.ones((width,height),np.uint32) * bg
		self.__opts['zbuffer'] = np.ones((width,height),np.float32) * 1e3
		pixels.shape = height,width
		
		# Handle Seg faults; seg faults in python are the reason I have trust issues
		def sig_handler(s,f):
			raise Exception("I'm so so so sorry... seg fault")
		signal.signal(signal.SIGSEGV,sig_handler)
		
		# Create an image from the pixel array
		self.__opts['image'] = Image.frombuffer('RGBA',(width,height),pixels,
											'raw','RGBA',0,1).convert('RGB')
		self.__opts['photo_image'] = ImageTk.PhotoImage(self.__opts['image'])
		
		# Draw the image to the canvas
		self.__opts['canvas'].create_image(width/2,height/2-20,
			image=self.__opts['photo_image'])		
			
	def __auto_refresh( self ):
		""" Automatically refreshes the canvas """
		if not self.__opts['update']: return
					
		else:
			# Display our performance stats
			dt = int(time.time() - self.__opts['start_time'])
			self.__opts['root'].title(''.join(['Lilac : ',
				str(self.__opts['fps']), ' fps','. Time: ',str(dt),
				'. Redraws: ',str(self.__opts['redraws'])]))
			
		# update the canvas
		mod_is_dirty = self.__opts['modules'][0]._is_dirty()
		if mod_is_dirty: 
			self.update_idletasks()

		# set to do it again
		self.__opts['root'].after( 1, self.__auto_refresh )
		
	def __init_draw_space( self ):
		""" Initializes the drawing information required by Modular
			scene design
		"""
		self.__opts.update( { 'GTM' : ViewTransformationMatrix(), 
			'camera' : View2D().setView2D(), 'ds' : DS(), 'lighting' : Lighting() } )
		self.texture = True # needs to be field for for fastest access
		self.fill = True # needs to be field for for fastest access
	
	def __apply_shadows( self ):
		""" Applies shadows to the canvas based on the root lighting,
			pixel information and depth buffer
		"""
		(lobj,pix,buf,cam) = self.config('lighting','pixels','zbuffer','camera')
		lobj.highlight_image(self)
		lobj.apply_shadows(pix,buf,cam)
	
from Module.IOC import ioc
ioc(globals()) # inverts the control
	
if __name__ == '__main__':
	print("\nLilakTk Tkinter Graphics Extension written by Matthew Levine 2014")