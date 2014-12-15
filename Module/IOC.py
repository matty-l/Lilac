"""
	This file contains a function that implements IOC (inversion
	of control) for any class that applies dependency injection.
	
	Author: Matthew Levine
	Date: 09/14/2014
"""
	
def ioc(globals):	
	""" Namespaces are fun, let's do more of those! """
	from Module.Shapes.ShapeFactory import shape_factory
	globals['shape_factory'] = shape_factory
	from Module.Lighting.Colors import Colors
	globals['Colors'] = Colors
