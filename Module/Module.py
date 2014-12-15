"""
	This file contains a class that does basic scene management.
			
	Author: Matthew Levine
	Date: 09/04/2014
"""

from Module.Shapes.Shape import NULL_SHAPE
from Module.Matrices.Matrix import ViewTransformationMatrix, IdentityMatrix
from Module.Lighting.DrawState import DrawState
import numpy as np

from Module.ModuleElement import ModuleElement
from Module.ClassUtils import Overrides

from tkinter.ttk import Progressbar, Label
from tkinter import Toplevel

import Lilac
from random import randint
import time

class Module(ModuleElement):
	""" This class holds any element that can be iteratively added to the scene.
		These elements are recognized by their abstract super class, 
		ModuleElement
	"""
	__id__ = 0
	
	def __init__( self ):
		ModuleElement.__init__(self)
		self.__elements__ = []
		
		self.id = ['Module',str(Module.__id__)]
		Module.__id__ += 1
		self.invisible = False # marks to some visitors that this should be skipped
	
	def draw_to_image( self, ltk, view_transformation_matrix = ViewTransformationMatrix(), 
			global_transformation_matrix = ViewTransformationMatrix(),
			draw_state = None, lighting = None):
		""" The call to a top-level module that iterates through its elements
			and requests that they modify the scene environment in some way.
			
			This method sets up the environment that module elements are allowed
			to modify. In the case of shapes, this modification would be a
			change in pixel values; in the case of camera changes, the change might
			be of a rotation to the VTM.
		"""
		
		# set up the drawing environment
		local_transformation_matrix = ViewTransformationMatrix()
		environment = locals()
		Lilac.set_polygon_fill(ltk.fill)
		[ shape.apply_to_scene( environment ) for shape in self.__elements__ ]
	
	@Overrides(ModuleElement)
	def apply_to_scene( self, environment ):
		""" Applies this module to the environment """
		if self.ignore: return
		(gtm,ltm) = (environment[key] for key in ('global_transformation_matrix',
			'local_transformation_matrix'))
		new_gtm = ViewTransformationMatrix()
		new_gtm.transform = np.dot(gtm.transform,ltm.transform)
		(ltk,vtm,ds,l) = (environment[key] for key in ('ltk',
			'view_transformation_matrix', 'draw_state','lighting'))
		Lilac.set_polygon_id( randint(1,10000) )
		self.draw_to_image( ltk, vtm, new_gtm, ds.copy(), l )		

	def add_shape( self, shape ):
		""" Attempts to add the given shape to the module. Returns it for
			chaining
		"""
		if shape.coordinates is not None:
			self.__elements__.append( shape )
			return shape
		else:
			raise ShapeImposterException("All shape classes must have coordinates")	
			
	def add_element( self, element ): 
		""" Adds a non-shape element to the module """
		if element == self: raise MobiusModulusException("Modules cannot be self-referential")
		self.__elements__.append( element )
		return element
	
	@Overrides(ModuleElement)
	def _is_dirty( self ):
		"""
			Returns True if any of the elements are dirty and necessitate 
			a redraw
		"""
		return any((el._is_dirty() for el in self.__elements__))
		
	@Overrides(ModuleElement)
	def _clean( self ):
		""" 
			Cleans all elements on the canvas, indicating that they do not need
			to be redrawn
		"""
		[ el._clean() for el in self.__elements__ ]
		
	def scale( self, sx, sy, sz ):
		""" Scales the module by sx, sy, and sz, i.e.,
			all shapes drawn after the addition of a scale matrix
			indicated by this method call will have their sizes
			altered along the bases with magnitude proportional to
			sx, sy, and sz.
		"""
		transform = ViewTransformationMatrix()
		transform.scale(sx,sy,sz)
		self.__elements__.append(transform)
		
	def rotate( self, cth, sth, axis ):
		""" Rotates the module along the given axis by the
			given amount provided as the cosine and sine of some 
			angle. All shapes drawn after the insertion of this
			transformation matrix will be rotated accordingly.
		"""
		Mtx = ViewTransformationMatrix
		m = Mtx()
		{'x':Mtx.rotateX,'y':Mtx.rotateY,'z':Mtx.rotateZ}[axis](m,cth,sth)
		self.__elements__.append(m)
		
	def translate( self, tx, ty, tz ):
		""" Translates the module by tx, ty, dz, i.e., all shapes
		drawn after the addition of the translation matrix
		implied by this method call will be translated by tx, ty,
		and tz.
		"""
		transform = ViewTransformationMatrix()
		transform.translate(tx,ty,tz)
		self.__elements__.append(transform)
		
	def identity( self ):
		""" Adds the identity reset matrix to the pipeline,
			indicating that the local transformation matrix should be 
			reset when indicator is reached by the draw queue
		"""
		self.__elements__.append(IdentityMatrix())

	def body_color( self, color ):
		""" Updates the body color of the module for all elements
			inserted by calls after this call
		"""
		self.__elements__.append(DrawState(base_color=color))
		
	def surface_color( self, color ):
		""" Updates the surface color of the module for all elements
			inserted by calls after this call
		"""
		self.__elements__.append(DrawState(surface_color=color))
		
	def opacity( self, alpha ):
		""" Updates the alpha level of the module for all elements inserted
			by calls after this call
		"""
		self.__elements__.append(DrawState(alpha=alpha))
		
	def wrap_queue( self ):
		""" Pushes the module queue so that the last element becomes the first
			element.
		"""
		self.__elements__.insert(0,self.__elements__[-1])
		self.__elements__.pop()
		
	def __repr__( self ):
		""" Returns a concise string representation of the module """
		return '<'+self.id[0]+' : '+self.id[1]+'>'
	
	@Overrides(ModuleElement)
	def accept( self, visitor ):
		""" Implements the visitor pattern for this module """
		return visitor.visit_module(self)
		
	def optimize( self ):
		""" Looks for patterns that can be consolidated """
		# fixme: export to visitor pattern

		removed_element_stack = []
		edited_elements_stack = {}
		cur_el = 0
		nex_el = 1
		cur = self.__elements__[0]
		while nex_el < len(self.__elements__):
			# if the same, increment the validator
			if cur_el == nex_el:
				nex_el += 1
				continue				
				
			# get the corresponding elements	
			cur = self.__elements__[cur_el]
			nex = self.__elements__[nex_el]
				
			if not ispoly(cur): # current is not a polygon
				cur_el += 1
				nex_el += 1
				cur = self.__elements__[cur_el]
			
			elif not ispoly(nex): # next one is not a polygon
				cur_el = next_el
				nex_el += 1
			else: # both are polygons spaced only by contiguous polygons
				if not cur_el in edited_elements_stack:
					# initialize local optimization stacks
					cur._coordump = [cur.coordinates]
					cur._normdump = [cur.normals]
					cur._colordump = [cur.texture]
					# mark that we've seen this one
					edited_elements_stack[cur_el] = 1

				cur._coordump.append(nex.coordinates)
				cur._normdump.append(nex.normals)
				cur._colordump.append(nex.texture)
									
				# save the position of the removed polygon
				removed_element_stack.append(nex_el) # don't concurrently modify loop
				
				nex_el += 1

		# consolidate optimized elements
		for index_of_optimized_item in edited_elements_stack.keys():
			cur = self.__elements__[index_of_optimized_item]
			cur.coordinates = np.array(cur._coordump)
			cur.normals = np.array(cur._normdump)
			cur.texture = np.array(cur._colordump)
				
		# remove consolidated items		
		for index_of_removed_item in reversed(removed_element_stack):			
			del self.__elements__[index_of_removed_item] 	

	def average_normals( self ):
		""" Applies Gouraud normalization to the module		
		"""
		# Set up updater
		top = Toplevel()
		pb = Progressbar(top,orient ="horizontal",length = 200, mode ="determinate")
		pb['maximum'] = len(self.__elements__)
		pb['value'] = 10
		pb.grid(row=0,column=0)
		tx = Label(top)
		tx.grid(row=1,column=0)
		top.update_idletasks()
		top.lift()
		t0 = time.time()
				
		# run the loop, if we're visible and phong shading
		if not self.invisible == 'gouroud':
			try:
				buf = np.array([0,0,0,1])
				for i,polygon in enumerate(self.__elements__):
					if not ispoly(polygon): continue
					polygon._onorms = np.array([polygon.normals.astype(float)+buf for i in range(len(polygon.coordinates))])
					
					# Update the user as to what's going on
					if i % 50 == 0 and i > 0:
						pb['value'] = i
						tmp = i/len(self.__elements__)
						estimation =  int(tmp*(time.time()-t0) * (1-tmp)/tmp)
						tx.configure(text=str(int(100*i/len(self.__elements__)))+"%"+' Estimated time: '+str(estimation)+'s' )
						top.update_idletasks()
						
					for c,coordinate in enumerate(polygon.coordinates):
						for j,opolygon in enumerate(self.__elements__):
							if i == j or not ispoly(opolygon): continue
							for k,ocoordinate in enumerate(opolygon.coordinates):
								if all(coordinate == ocoordinate): # same vertex, finally
									polygon._onorms[c] += (opolygon.normals+buf)
					polygon._onorms /= polygon._onorms[:,3,None]
					
				for polygon in self.__elements__:
					if ispoly(polygon): 
						polygon.normals = polygon._onorms
						del polygon._onorms
			except IndexError as ie: pass
		
		top.destroy()
		
		if self.invisible == 'gouroud':
			self.invisible = False
		return self # for chaining
		
class MobiusModulusException(Exception): pass

def ispoly(obj): 
	try: obj.texture; return 1
	except: return 0