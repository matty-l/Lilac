"""
	This file contains a class that employs the visitor pattern to gather
	display information for a table.
	
	Author: Matthew Levine
	Date: 09/20/2014

"""

from Module.Visitors.Visitor import Visitor
from Module.ClassUtils import Overrides
from Module.Shapes.Polygon import NULL_POLYGON, Polygon

typecheck = lambda obj1, obj2 : isinstance(obj1,Polygon) # not OO cool but ok

IGNORE_POLYGONS = True
def ignore_polygons( flag ):
	""" Sets whether to ignore polygons """
	global IGNORE_POLYGONS
	IGNORE_POLYGONS = flag

class TableVisitor(Visitor):
	""" This class uses double dispatch to gather display information
		for tables
	"""
	
	def get_table_info( self, root, exclusions = {} ):
		self.display_info =  []
		self.master_stack = ['']
		self.exclusions = exclusions
		root.accept( self )
		return self
	
	@Overrides(Visitor)
	def visit_module( self, module ):
		""" Gathers the appropriate information from a module """
		mod_len = len(module.__elements__)

		if not ( module in self.exclusions and self.exclusions[module] ):
			self.master_stack.append(module)
			[element.accept(self) for element in module.__elements__]
			self.master_stack.pop()
		if not module.invisible:
			self.display_info.append( [module,mod_len,self.master_stack[-1]] )

	@Overrides(Visitor)
	def visit_polygon( self, poly ):
		""" Adds a polygon to the table, but only displays 3 at a time
			as not to crowd the table with 1e100 polygons at a time
		"""
		if IGNORE_POLYGONS: return
		chart = self.display_info
		if len(chart) > 4 and all([typecheck(info[0], poly) for info in chart[-3:]]):
			chart[-2] = [NULL_POLYGON,'...',self.master_stack[-1]]
			return None
		
		coords = poly.coordinates 
		chart.append([poly,len(coords),self.master_stack[-1]])
		
	@Overrides(Visitor)
	def visit_matrix( self, mtx ):
		""" Adds a matrix to the table """
		return
		# mtx_len = sum([item!=0 for item in mtx.transform.flatten()])
		# self.display_info.append([mtx,mtx_len,self.master_stack[-1]])
		
		
	